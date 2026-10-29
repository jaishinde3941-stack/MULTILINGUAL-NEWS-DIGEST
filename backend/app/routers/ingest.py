from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.database import get_db, SessionLocal
from app.models.article import Article
from app.schemas.article import IngestResult
from app.services.scraper import scraper, CURATED_RSS_FEEDS
from app.services.llm_pipeline import llm_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingest", tags=["Ingestion & Pipeline"])

def run_ingestion_job(max_per_feed: int = 2):
    """Background ingestion task: scrapes RSS and executes LLM translation & tagging."""
    db = SessionLocal()
    try:
        raw_items = scraper.scrape_all(max_per_feed=max_per_feed)
        for item in raw_items:
            # Check if already ingested
            exists = db.query(Article).filter(Article.source_url == item["source_url"]).first()
            if exists:
                continue

            try:
                processed = llm_pipeline.process_article(
                    title=item["title"],
                    content=item["content"],
                    source_name=item["source_name"],
                    source_url=item["source_url"],
                    expected_language=item.get("expected_language"),
                    expected_region=item.get("expected_region")
                )

                art = Article(
                    source_url=item["source_url"],
                    source_name=item["source_name"],
                    original_language=processed["language"],
                    original_title=item["title"],
                    original_content=item["content"],
                    original_summary=None,
                    english_title=processed["english_title"],
                    english_summary=processed["english_summary"],
                    english_content=processed["english_content"],
                    region=processed["region"],
                    subregion=processed.get("subregion"),
                    field=processed["field"],
                    keywords=processed["keywords"],
                    trending=processed["trending"],
                    trending_score=processed["trending_score"],
                    image_url=item.get("image_url"),
                    published_at=item.get("published_at")
                )
                db.add(art)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error processing article {item['source_url']}: {e}")
    finally:
        db.close()

@router.post("/trigger", response_model=IngestResult)
def trigger_ingest(
    background_tasks: BackgroundTasks,
    max_per_feed: int = Query(2, ge=1, le=10),
    run_async: bool = Query(True)
):
    """
    Trigger the scraper & local Ollama LLM translation pipeline.
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
                exists = db.query(Article).filter(Article.source_url == item["source_url"]).first()
                if exists:
                    skipped += 1
                    continue
                try:
                    p = llm_pipeline.process_article(
                        title=item["title"],
                        content=item["content"],
                        source_name=item["source_name"],
                        source_url=item["source_url"],
                        expected_language=item.get("expected_language"),
                        expected_region=item.get("expected_region")
                    )
                    art = Article(
                        source_url=item["source_url"],
                        source_name=item["source_name"],
                        original_language=p["language"],
                        original_title=item["title"],
                        original_content=item["content"],
                        original_summary=None,
                        english_title=p["english_title"],
                        english_summary=p["english_summary"],
                        english_content=p["english_content"],
                        region=p["region"],
                        subregion=p.get("subregion"),
                        field=p["field"],
                        keywords=p["keywords"],
                        trending=p["trending"],
                        trending_score=p["trending_score"],
                        image_url=item.get("image_url"),
                        published_at=item.get("published_at")
                    )
                    db.add(art)
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

@router.get("/sources")
def list_curated_sources() -> List[Dict[str, Any]]:
    """List all configured international RSS feeds."""
    return CURATED_RSS_FEEDS
