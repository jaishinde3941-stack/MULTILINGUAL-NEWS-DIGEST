import threading
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func

from app.database import SessionLocal, engine
from app.models.article import Article
from app.models.history import ArticleHistory
from app.services.scraper import scraper
from app.services.llm_pipeline import llm_pipeline
from app.services.dedup import normalize_canonical_url, compute_article_fingerprint, is_duplicate_article

logger = logging.getLogger("news_digest.ingestion_manager")

TARGET_BATCH_SIZE = 50
MAX_CONSUMED_RETAINED = 200

class IngestionManager:
    """
    Manages the two-batch prefetching lifecycle:
    - Active Batch (Batch A): 50 articles displayed to users.
    - Reserve Batch (Batch B): 50 articles prepared in background.
    - Atomic Rotation: Instantly swaps reserve to active, retires active to consumed.
    - Durable Background Refill: Continuously prepares replacement reserve batches.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._is_refilling = False
        self._refill_thread: Optional[threading.Thread] = None
        self._progress: Dict[str, Any] = {
            "status": "idle",
            "ready": 0,
            "target": TARGET_BATCH_SIZE,
            "message": "System ready"
        }

    def get_status(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """Query real-time metrics for active, reserve, and consumed articles."""
        close_db = False
        if db_session is not None:
            db = db_session
        else:
            db = SessionLocal()
            close_db = True
        try:
            active_count = db.query(Article).filter(
                Article.batch_state == "active",
                Article.processing_status == "completed"
            ).count()

            reserve_count = db.query(Article).filter(
                Article.batch_state == "reserve",
                Article.processing_status == "completed"
            ).count()

            consumed_count = db.query(Article).filter(
                Article.batch_state == "consumed"
            ).count()

            history_count = db.query(ArticleHistory).count()

            active_batch_art = db.query(Article.batch_id).filter(
                Article.batch_state == "active",
                Article.processing_status == "completed"
            ).order_by(desc(Article.displayed_at), desc(Article.id)).first()
            active_batch_id = active_batch_art[0] if active_batch_art and active_batch_art[0] else None

            can_rotate = reserve_count >= TARGET_BATCH_SIZE

            return {
                "active_count": active_count,
                "reserve_count": reserve_count,
                "consumed_count": consumed_count,
                "history_count": history_count,
                "target_batch_size": TARGET_BATCH_SIZE,
                "active_batch_id": active_batch_id,
                "is_refilling": self._is_refilling,
                "can_rotate": can_rotate,
                "refill_progress": {
                    "status": self._progress["status"],
                    "ready": reserve_count,
                    "current": reserve_count,
                    "target": TARGET_BATCH_SIZE,
                    "message": self._progress["message"]
                }
            }
        finally:
            if close_db:
                db.close()

    def on_startup(self):
        """
        Invoked on FastAPI application startup.
        Inspects existing inventory and initiates prefetching if active or reserve batches
        are below the 50-article capacity.
        """
        logger.info("Initializing IngestionManager startup verification...")
        status = self.get_status()
        active = status["active_count"]
        reserve = status["reserve_count"]

        logger.info(f"Startup Inventory: {active} active articles, {reserve} reserve articles.")

        # If database has existing completed articles but batch_state wasn't initialized
        db = SessionLocal()
        try:
            unassigned_count = db.query(Article).filter(
                or_(Article.batch_state.is_(None), Article.batch_state == "")
            ).count()

            if unassigned_count > 0 and active == 0:
                logger.info(f"Assigning {unassigned_count} legacy articles to initial active and reserve batches...")
                completed_articles = db.query(Article).filter(
                    Article.processing_status == "completed"
                ).order_by(desc(Article.published_at)).all()

                for idx, art in enumerate(completed_articles):
                    if not art.canonical_url:
                        art.canonical_url = normalize_canonical_url(art.source_url)
                    if not art.article_fingerprint:
                        art.article_fingerprint = compute_article_fingerprint(
                            art.original_title, art.source_name, art.canonical_url
                        )

                    if idx < TARGET_BATCH_SIZE:
                        art.batch_state = "active"
                        art.batch_id = "initial_active_batch"
                        art.displayed_at = art.displayed_at or datetime.now(timezone.utc)
                    elif idx < TARGET_BATCH_SIZE * 2:
                        art.batch_state = "reserve"
                        art.batch_id = "initial_reserve_batch"
                    else:
                        art.batch_state = "consumed"
                        art.consumed_at = art.consumed_at or datetime.now(timezone.utc)
                db.commit()
                status = self.get_status()
                active = status["active_count"]
                reserve = status["reserve_count"]
        except Exception as e:
            db.rollback()
            logger.warning(f"Legacy inventory assignment notice: {e}")
        finally:
            db.close()

        # Trigger background prefetching if active or reserve need filling
        if active < TARGET_BATCH_SIZE or reserve < TARGET_BATCH_SIZE:
            logger.info("Active or reserve batch below target capacity (50). Starting background prefetch...")
            self.trigger_refill()
        else:
            logger.info("System is in ready steady state (50 active, 50 reserve). No startup scraping needed.")

    def trigger_refill(self) -> Dict[str, Any]:
        """
        Start a background refill worker thread if not already running.
        Idempotent: prevents duplicate threads.
        """
        with self._lock:
            if self._is_refilling:
                return {
                    "status": "already_refilling",
                    "message": "Background refill is already in progress.",
                    "progress": self._progress
                }

            self._is_refilling = True
            self._progress = {
                "status": "starting",
                "ready": 0,
                "target": TARGET_BATCH_SIZE,
                "message": "Starting background news prefetching..."
            }

            self._refill_thread = threading.Thread(
                target=self._run_refill_worker,
                daemon=True,
                name="news-digest-refill-worker"
            )
            self._refill_thread.start()

            return {
                "status": "started",
                "message": "Background refill worker initiated.",
                "progress": self._progress
            }

    def _run_refill_worker(self):
        """
        Durable background worker:
        1. Checks current active and reserve deficits.
        2. Scrapes parallel RSS feeds for fresh candidates.
        3. Deduplicates against active, reserve, and historical records.
        4. Summarizes candidates via local Ollama Llama 3.2.
        5. Saves completed articles with batch_state='reserve' (or 'active' if empty).
        """
        logger.info("Background refill worker started.")
        batch_id = f"batch_{int(time.time())}_{uuid.uuid4().hex[:6]}"

        try:
            db = SessionLocal()
            try:
                active_count = db.query(Article).filter(
                    Article.batch_state == "active",
                    Article.processing_status == "completed"
                ).count()

                reserve_count = db.query(Article).filter(
                    Article.batch_state == "reserve",
                    Article.processing_status == "completed"
                ).count()
            finally:
                db.close()

            # Target is to ensure active has 50, and reserve has 50
            needed_active = max(0, TARGET_BATCH_SIZE - active_count)
            needed_reserve = max(0, TARGET_BATCH_SIZE - reserve_count)
            total_needed = needed_active + needed_reserve

            if total_needed == 0:
                logger.info("Both active and reserve batches are already at capacity (50/50). Refill complete.")
                with self._lock:
                    self._is_refilling = False
                    self._progress = {
                        "status": "idle",
                        "ready": TARGET_BATCH_SIZE,
                        "target": TARGET_BATCH_SIZE,
                        "message": "Batches are full (50 active, 50 reserve)."
                    }
                return

            self._progress["status"] = "scraping"
            self._progress["message"] = f"Scraping international feeds to gather {total_needed} articles..."

            # 1. Fetch raw items from feeds with dynamic per-feed depth
            scrape_depth = max(15, (total_needed // 4) + 6)
            raw_candidates = scraper.scrape_all(max_per_feed=scrape_depth, max_workers=8)
            logger.info(f"Gathered {len(raw_candidates)} candidate articles across international feeds (depth={scrape_depth}).")

            # 2. Filter duplicates using canonical URLs and fingerprints
            unique_candidates: List[Dict[str, Any]] = []
            seen_in_batch = set()

            db = SessionLocal()
            try:
                for item in raw_candidates:
                    c_url = item.get("canonical_url") or normalize_canonical_url(item["source_url"])
                    fg = item.get("fingerprint") or compute_article_fingerprint(item["title"], item["source_name"], c_url)

                    if fg in seen_in_batch or c_url in seen_in_batch:
                        continue
                    seen_in_batch.add(fg)
                    seen_in_batch.add(c_url)

                    # Deduplication pre-check
                    if is_duplicate_article(db, c_url, fg, item["source_url"]):
                        continue

                    item["canonical_url"] = c_url
                    item["fingerprint"] = fg
                    unique_candidates.append(item)
            finally:
                db.close()

            # Deep scrape fallback if initial pass is below required candidates
            if len(unique_candidates) < total_needed:
                logger.info(f"Initial pass yielded {len(unique_candidates)} unique candidates (< {total_needed} needed). Scraping deeper with max_per_feed=25...")
                deep_raw = scraper.scrape_all(max_per_feed=25, max_workers=8)
                db = SessionLocal()
                try:
                    for item in deep_raw:
                        c_url = item.get("canonical_url") or normalize_canonical_url(item["source_url"])
                        fg = item.get("fingerprint") or compute_article_fingerprint(item["title"], item["source_name"], c_url)

                        if fg in seen_in_batch or c_url in seen_in_batch:
                            continue
                        seen_in_batch.add(fg)
                        seen_in_batch.add(c_url)

                        if is_duplicate_article(db, c_url, fg, item["source_url"]):
                            continue

                        item["canonical_url"] = c_url
                        item["fingerprint"] = fg
                        unique_candidates.append(item)
                finally:
                    db.close()

            logger.info(f"Identified {len(unique_candidates)} unique, unconsumed news candidates.")

            # Prefer newly published items
            unique_candidates.sort(
                key=lambda x: x.get("published_at") or datetime.fromtimestamp(0, tz=timezone.utc),
                reverse=True
            )

            # 3. Process candidates through Ollama Llama 3.2
            processed_in_job = 0
            self._progress["status"] = "summarizing"

            for item in unique_candidates:
                # Re-check status in case batch was rotated while processing
                db = SessionLocal()
                try:
                    current_active = db.query(Article).filter(
                        Article.batch_state == "active",
                        Article.processing_status == "completed"
                    ).count()
                    current_reserve = db.query(Article).filter(
                        Article.batch_state == "reserve",
                        Article.processing_status == "completed"
                    ).count()
                finally:
                    db.close()

                # Determine target state for this article:
                # If active batch is below 50, prioritize populating active so users have news immediately!
                if current_active < TARGET_BATCH_SIZE:
                    target_state = "active"
                elif current_reserve < TARGET_BATCH_SIZE:
                    target_state = "reserve"
                else:
                    # Both are satisfied
                    break

                self._progress["message"] = (
                    f"Processing with Llama 3.2 ({current_reserve}/{TARGET_BATCH_SIZE} reserve ready)..."
                )

                # Create pending article record
                db = SessionLocal()
                art_id = None
                try:
                    article_batch_id = batch_id
                    if target_state == "active":
                        active_b = db.query(Article.batch_id).filter(
                            Article.batch_state == "active",
                            Article.processing_status == "completed"
                        ).order_by(desc(Article.displayed_at), desc(Article.id)).first()
                        if active_b and active_b[0]:
                            article_batch_id = active_b[0]

                    art = Article(
                        source_url=item["source_url"],
                        canonical_url=item["canonical_url"],
                        article_fingerprint=item["fingerprint"],
                        source_name=item["source_name"],
                        original_language=item.get("expected_language") or "English",
                        original_title=item["title"],
                        original_content=item["content"],
                        original_summary=None,
                        english_title=item["title"],
                        english_summary="Generating English summary...",
                        english_content="Generating...",
                        region=item.get("expected_region") or "Global",
                        subregion=None,
                        field="General News",
                        keywords=[],
                        trending=False,
                        trending_score=0.5,
                        processing_status="pending",
                        processing_error=None,
                        summary_word_count=0,
                        batch_id=article_batch_id,
                        batch_state=target_state,
                        image_url=item.get("image_url"),
                        published_at=item.get("published_at"),
                        displayed_at=datetime.now(timezone.utc) if target_state == "active" else None
                    )
                    db.add(art)
                    db.commit()
                    db.refresh(art)
                    art_id = art.id

                    # Run LLM Pipeline
                    p = llm_pipeline.process_article(
                        title=art.original_title,
                        content=art.original_content,
                        source_name=art.source_name,
                        source_url=art.source_url,
                        expected_language=item.get("expected_language"),
                        expected_region=item.get("expected_region"),
                        article_id=art.id
                    )

                    art.original_language = p["language"]
                    art.english_title = p["english_title"]
                    art.english_summary = p["english_summary"]
                    art.english_content = p["english_content"]
                    art.region = p["region"]
                    art.subregion = p.get("subregion")
                    art.field = p["field"]
                    art.keywords = p["keywords"]
                    art.trending = p["trending"]
                    art.trending_score = p["trending_score"]
                    art.processing_status = p.get("processing_status", "completed")
                    art.processing_error = p.get("processing_error")
                    art.summary_word_count = p.get("summary_word_count", len(p["english_summary"].split()))

                    db.commit()
                    processed_in_job += 1
                    logger.info(f"Prepared article {art.id} for {target_state} batch: {art.english_title[:40]} [{art.processing_status}]")
                except Exception as ex:
                    db.rollback()
                    logger.warning(f"Error processing candidate article: {ex}")
                finally:
                    db.close()

            logger.info(f"Background refill finished. Processed {processed_in_job} articles.")
        except Exception as e:
            logger.error(f"Background refill worker exception: {e}")
        finally:
            with self._lock:
                self._is_refilling = False
                st = self.get_status()
                self._progress = {
                    "status": "idle",
                    "ready": st["reserve_count"],
                    "target": TARGET_BATCH_SIZE,
                    "message": f"Refill cycle complete ({st['reserve_count']}/{TARGET_BATCH_SIZE} reserve ready)."
                }

    def _cleanup_consumed_payloads(self, db: Session, max_retained: int = MAX_CONSUMED_RETAINED, now_utc: Optional[datetime] = None):
        """Clean up obsolete consumed article payloads beyond retention limit while preserving ArticleHistory."""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        consumed_count = db.query(Article).filter(Article.batch_state == "consumed").count()
        if consumed_count > max_retained:
            excess = consumed_count - max_retained
            old_consumed = db.query(Article).filter(
                Article.batch_state == "consumed"
            ).order_by(Article.consumed_at.asc()).limit(excess).all()

            seen_cleanup_fps = set()
            for old_art in old_consumed:
                c_url = old_art.canonical_url or normalize_canonical_url(old_art.source_url)
                fg = old_art.article_fingerprint or compute_article_fingerprint(old_art.original_title, old_art.source_name, c_url)
                
                if fg not in seen_cleanup_fps:
                    seen_cleanup_fps.add(fg)
                    hist_exists = db.query(ArticleHistory.id).filter(ArticleHistory.fingerprint == fg).first()
                    if not hist_exists:
                        try:
                            db.add(ArticleHistory(
                                article_id=old_art.id,
                                canonical_url=c_url,
                                fingerprint=fg,
                                title=(old_art.original_title or "")[:500],
                                source_name=old_art.source_name or "Unknown",
                                consumed_at=old_art.consumed_at or now_utc
                            ))
                        except Exception as hex:
                            logger.warning(f"Could not archive history for old article {old_art.id}: {hex}")
                db.delete(old_art)
            logger.info(f"Cleaned up {len(old_consumed)} obsolete consumed article records.")

    def rotate_batch(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Perform fast atomic batch rotation:
        1. Verify that the reserve batch has ready articles.
        2. If ready:
           - Mark currently active articles as 'consumed'.
           - Insert deduplication records into ArticleHistory.
           - Promote reserve articles to 'active'.
           - Clean up obsolete consumed article payloads.
           - Trigger background refill for the next reserve batch.
        3. If not ready:
           - Keep current active batch visible.
           - Return refill-in-progress status without blocking.
        """
        with self._lock:
            close_db = False
            if db_session is not None:
                db = db_session
            else:
                db = SessionLocal()
                close_db = True

            try:
                # 1. Count completed reserve articles
                reserve_articles = db.query(Article).filter(
                    Article.batch_state == "reserve",
                    Article.processing_status == "completed"
                ).order_by(desc(Article.published_at)).limit(TARGET_BATCH_SIZE).all()

                reserve_count = len(reserve_articles)

                active_batch_art = db.query(Article.batch_id).filter(
                    Article.batch_state == "active",
                    Article.processing_status == "completed"
                ).order_by(desc(Article.displayed_at), desc(Article.id)).first()
                current_active_batch_id = active_batch_art[0] if active_batch_art and active_batch_art[0] else None

                # Query current active articles so they are always returned even when refill is in progress
                active_articles_current = db.query(Article).filter(
                    Article.batch_state == "active",
                    Article.processing_status == "completed"
                ).order_by(desc(Article.trending), desc(Article.trending_score), desc(Article.published_at)).limit(TARGET_BATCH_SIZE).all()

                if not active_articles_current:
                    active_articles_current = db.query(Article).filter(
                        Article.processing_status == "completed"
                    ).order_by(desc(Article.published_at)).limit(TARGET_BATCH_SIZE).all()

                from app.schemas.article import ArticleResponse
                current_active_items = [ArticleResponse.model_validate(art) for art in active_articles_current]

                if reserve_count < TARGET_BATCH_SIZE:
                    # Shortage: keep current batch visible, return progress AND current active articles
                    active_count = len(current_active_items)

                    # Trigger refill if not already working
                    if not self._is_refilling:
                        threading.Thread(target=self._run_refill_worker, daemon=True, name="refill-worker").start()
                        self._is_refilling = True

                    return {
                        "status": "refill_in_progress",
                        "message": f"Preparing replacement articles in background ({reserve_count}/{TARGET_BATCH_SIZE} ready). Current active news retained.",
                        "batch_id": current_active_batch_id,
                        "active_batch_id": current_active_batch_id,
                        "ready_count": reserve_count,
                        "target": TARGET_BATCH_SIZE,
                        "active_count": active_count,
                        "rotated_count": 0,
                        "count": active_count,
                        "reserve_count": reserve_count,
                        "reserve_remaining": reserve_count,
                        "items": current_active_items,
                        "articles": current_active_items,
                        "is_refilling": self._is_refilling
                    }

                # 2. Atomic Rotation in a single database transaction
                now_utc = datetime.now(timezone.utc)
                new_batch_id = f"batch_{int(time.time())}_{uuid.uuid4().hex[:6]}"
                active_articles = db.query(Article).filter(
                    Article.batch_state == "active"
                ).all()

                seen_fingerprints = set()
                # Archive active articles to consumed and record history
                for art in active_articles:
                    art.batch_state = "consumed"
                    art.consumed_at = now_utc

                    # Save to permanent ArticleHistory
                    c_url = art.canonical_url or normalize_canonical_url(art.source_url)
                    fg = art.article_fingerprint or compute_article_fingerprint(art.original_title, art.source_name, c_url)
                    
                    if fg in seen_fingerprints:
                        continue
                    seen_fingerprints.add(fg)

                    hist_exists = db.query(ArticleHistory.id).filter(
                        ArticleHistory.fingerprint == fg
                    ).first()

                    if not hist_exists:
                        try:
                            hist = ArticleHistory(
                                article_id=art.id,
                                canonical_url=c_url,
                                fingerprint=fg,
                                title=(art.original_title or "")[:500],
                                source_name=art.source_name or "Unknown",
                                consumed_at=now_utc
                            )
                            db.add(hist)
                        except Exception as hex:
                            logger.warning(f"Could not stage article history for {art.id}: {hex}")

                # Promote reserve articles to active
                for res_art in reserve_articles:
                    res_art.batch_state = "active"
                    res_art.batch_id = new_batch_id
                    res_art.displayed_at = now_utc

                # 3. Clean up obsolete consumed article payloads beyond retention limit
                self._cleanup_consumed_payloads(db, now_utc=now_utc)
                db.commit()

                # Validate and serialize models into Pydantic while session is still alive!
                from app.schemas.article import ArticleResponse
                rotated_items = [ArticleResponse.model_validate(art) for art in reserve_articles]
                logger.info(f"Rotated {len(rotated_items)} reserve articles into active batch ID {new_batch_id}.")
            except Exception as e:
                db.rollback()
                logger.error(f"Batch rotation failed: {e}")
                raise e
            finally:
                if close_db:
                    db.close()

            # 4. Automatically trigger background refill to prepare replacement reserve batch
            if not self._is_refilling:
                threading.Thread(target=self._run_refill_worker, daemon=True, name="refill-worker").start()
                self._is_refilling = True

            st = self.get_status()
            return {
                "status": "rotated",
                "message": f"Successfully activated fresh news batch of {len(rotated_items)} articles.",
                "batch_id": new_batch_id,
                "active_batch_id": new_batch_id,
                "rotated_count": len(rotated_items),
                "count": len(rotated_items),
                "active_count": st["active_count"],
                "reserve_count": st["reserve_count"],
                "reserve_remaining": st["reserve_count"],
                "ready_count": st["reserve_count"],
                "items": rotated_items,
                "articles": rotated_items,
                "is_refilling": True
            }

ingestion_manager = IngestionManager()
