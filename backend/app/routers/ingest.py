from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db, SessionLocal
from app.models.article import Article
from app.schemas.article import IngestResult
from app.services.scraper import scraper, CURATED_RSS_FEEDS
from app.services.llm_pipeline import llm_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingest", tags=["Ingestion & Pipeline"])

def run_ingestion_job(max_per_feed: int = 2):
    """
    Background ingestion task: scrapes RSS and executes Ollama Llama 3.2 summarization & tagging.
    Ties each LLM call to the article record and prevents race conditions.
    """
    db = SessionLocal()
    try:
        raw_items = scraper.scrape_all(max_per_feed=max_per_feed)
        for item in raw_items:
            # Check if already ingested and completed
            existing = db.query(Article).filter(Article.source_url == item["source_url"]).first()
            if existing and getattr(existing, "processing_status", "completed") == "completed":
                continue

            try:
                # 1. Create or retrieve article with 'pending' status
                if not existing:
                    art = Article(
                        source_url=item["source_url"],
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
                        image_url=item.get("image_url"),
                        published_at=item.get("published_at")
                    )
                    db.add(art)
                    db.commit()
                    db.refresh(art)
                else:
                    art = existing
                    art.processing_status = "pending"
                    db.commit()

                # 2. Run LLM Pipeline with the specific article ID
                processed = llm_pipeline.process_article(
                    title=art.original_title,
                    content=art.original_content,
                    source_name=art.source_name,
                    source_url=art.source_url,
                    expected_language=item.get("expected_language"),
                    expected_region=item.get("expected_region"),
                    article_id=art.id
                )

                # 3. Update the exact record with generated headline, summary, and status
                art.original_language = processed["language"]
                art.english_title = processed["english_title"]
                art.english_summary = processed["english_summary"]
                art.english_content = processed["english_content"]
                art.region = processed["region"]
                art.subregion = processed.get("subregion")
                art.field = processed["field"]
                art.keywords = processed["keywords"]
                art.trending = processed["trending"]
                art.trending_score = processed["trending_score"]
                art.processing_status = processed.get("processing_status", "completed")
                art.processing_error = processed.get("processing_error")
                art.summary_word_count = processed.get("summary_word_count", len(processed["english_summary"].split()))

                db.commit()
                logger.info(f"Successfully processed article {art.id}: {art.english_title[:40]} [{art.processing_status}]")
            except Exception as e:
                db.rollback()
                logger.error(f"Error processing article {item['source_url']}: {e}")
    finally:
        db.close()

def run_reprocess_job(limit: int = 25, mode: str = "unprocessed"):
    """
    Safely reprocess failed, flagged, or placeholder-summary articles in the background.
    Preserves already-correct completed articles.
    """
    db = SessionLocal()
    try:
        query = db.query(Article)
        if mode == "failed_only":
            query = query.filter(Article.processing_status == "failed")
        else:
            # Reprocess failed, flagged, pending, or boilerplate placeholder summaries
            query = query.filter(
                or_(
                    Article.processing_status.in_(["failed", "flagged", "pending"]),
                    Article.english_summary.ilike("%Verified dispatch%"),
                    Article.english_summary.ilike("%A major development has been reported%"),
                    Article.english_summary.ilike("%queued for local model processing%")
                )
            )
        
        articles_to_reprocess = query.limit(limit).all()
        logger.info(f"Starting background reprocessing for {len(articles_to_reprocess)} articles.")

        for art in articles_to_reprocess:
            try:
                art.processing_status = "pending"
                db.commit()

                processed = llm_pipeline.process_article(
                    title=art.original_title,
                    content=art.original_content,
                    source_name=art.source_name,
                    source_url=art.source_url,
                    expected_language=art.original_language,
                    expected_region=art.region,
                    article_id=art.id
                )

                art.original_language = processed["language"]
                art.english_title = processed["english_title"]
                art.english_summary = processed["english_summary"]
                art.english_content = processed["english_content"]
                art.region = processed.get("region", art.region)
                art.field = processed.get("field", art.field)
                art.keywords = processed.get("keywords", art.keywords)
                art.trending = processed.get("trending", art.trending)
                art.trending_score = processed.get("trending_score", art.trending_score)
                art.processing_status = processed.get("processing_status", "completed")
                art.processing_error = processed.get("processing_error")
                art.summary_word_count = processed.get("summary_word_count", len(processed["english_summary"].split()))

                db.commit()
                logger.info(f"Reprocessed article {art.id}: status={art.processing_status}")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to reprocess article {art.id}: {e}")
    finally:
        db.close()

@router.post("/trigger", response_model=IngestResult)
def trigger_ingest(
    background_tasks: BackgroundTasks,
    max_per_feed: int = Query(2, ge=1, le=10),
    run_async: bool = Query(True)
):
    """
    Trigger the scraper & local Ollama LLM summarization pipeline.
    Runs asynchronously in background by default, or synchronously if run_async=False.
    """
    if run_async:
        background_tasks.add_task(run_ingestion_job, max_per_feed=max_per_feed)
        return IngestResult(
            scraped_count=len(CURATED_RSS_FEEDS) * max_per_feed,
            processed_count=0,
            skipped_count=0,
            errors=["Ingestion scheduled in background tasks"]
        )
    else:
        # Run synchronous
        db = SessionLocal()
        scraped = 0
        processed = 0
        skipped = 0
        errors = []
        try:
            raw_items = scraper.scrape_all(max_per_feed=max_per_feed)
            scraped = len(raw_items)
            for item in raw_items:
                existing = db.query(Article).filter(Article.source_url == item["source_url"]).first()
                if existing and getattr(existing, "processing_status", "completed") == "completed":
                    skipped += 1
                    continue
                try:
                    if not existing:
                        art = Article(
                            source_url=item["source_url"],
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
                            image_url=item.get("image_url"),
                            published_at=item.get("published_at")
                        )
                        db.add(art)
                        db.commit()
                        db.refresh(art)
                    else:
                        art = existing

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
                    processed += 1
                except Exception as ex:
                    db.rollback()
                    errors.append(str(ex))
        finally:
            db.close()

        return IngestResult(
            scraped_count=scraped,
            processed_count=processed,
            skipped_count=skipped,
            errors=errors
        )

@router.post("/reprocess")
def trigger_reprocess(
    background_tasks: BackgroundTasks,
    limit: int = Query(25, ge=1, le=100),
    mode: str = Query("unprocessed", description="unprocessed (failed/flagged/pending/placeholder) or failed_only"),
    run_async: bool = Query(True)
):
    """Safely reprocess failed, flagged, or incomplete articles."""
    if run_async:
        background_tasks.add_task(run_reprocess_job, limit=limit, mode=mode)
        return {"status": "scheduled", "message": f"Reprocessing up to {limit} articles in background", "mode": mode}
    else:
        run_reprocess_job(limit=limit, mode=mode)
        return {"status": "completed", "message": f"Reprocessed up to {limit} articles", "mode": mode}

@router.get("/status")
def get_ingest_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve database article processing and quality metrics."""
    total = db.query(Article).count()
    completed = db.query(Article).filter(Article.processing_status == "completed").count()
    pending = db.query(Article).filter(Article.processing_status == "pending").count()
    failed = db.query(Article).filter(Article.processing_status == "failed").count()
    flagged = db.query(Article).filter(Article.processing_status == "flagged").count()
    
    return {
        "total_articles": total,
        "completed": completed,
        "pending": pending,
        "failed": failed,
        "flagged": flagged,
        "ollama_status": llm_pipeline.check_ollama_status()
    }

@router.get("/sources")
def list_curated_sources() -> List[Dict[str, Any]]:
    """List all configured international RSS feeds."""
    return CURATED_RSS_FEEDS
