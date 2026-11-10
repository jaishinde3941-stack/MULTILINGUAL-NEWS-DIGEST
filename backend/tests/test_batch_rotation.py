"""
Unit and integration tests for the two-batch news ingestion, prefetching,
deduplication, and automatic rotation architecture.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models.article import Article
from app.models.history import ArticleHistory
from app.services.dedup import normalize_canonical_url, compute_article_fingerprint, is_duplicate_article
from app.services.ingestion_manager import IngestionManager
from app.main import app

# Create in-memory SQLite database for isolated batch tests
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _create_mock_article(idx: int, batch_state: str = "active", batch_id: str = "batch_init_1") -> Article:
    url = f"https://example.com/news/article-{idx}?utm_source=test"
    canonical = f"https://example.com/news/article-{idx}"
    title = f"Test News Article #{idx}"
    source = "Global Gazette"
    fingerprint = compute_article_fingerprint(title, source, canonical)
    return Article(
        source_url=url,
        canonical_url=canonical,
        article_fingerprint=fingerprint,
        source_name=source,
        original_language="Spanish",
        original_title=title,
        original_content=f"Original content for article #{idx} with enough text for verification.",
        original_summary="Original Spanish summary content",
        english_title=f"English Headline #{idx}",
        english_summary=f"English executive summary for article #{idx} formatted with exactly 80 to 120 words of factual context.",
        english_content=f"Full English content for #{idx}",
        region="Latin America",
        field="Politics",
        keywords=["global", "policy"],
        trending=True,
        trending_score=85,
        processing_status="completed",
        summary_word_count=95,
        batch_id=batch_id,
        batch_state=batch_state,
        published_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# 1. Deduplication Service Tests
# ---------------------------------------------------------------------------
def test_normalize_canonical_url():
    dirty_url = "https://www.example.com/world/news?id=123&utm_source=newsletter&utm_medium=email&fbclid=XYZ#"
    normalized = normalize_canonical_url(dirty_url)
    assert "utm_source" not in normalized
    assert "utm_medium" not in normalized
    assert "fbclid" not in normalized
    assert "id=123" in normalized
    assert normalized.startswith("https://www.example.com/world/news")


def test_compute_article_fingerprint():
    title = "Breaking: Historic Accord Signed"
    source = "Global Gazette"
    canonical = "https://example.com/news/historic-accord"
    fp1 = compute_article_fingerprint(title, source, canonical)
    fp2 = compute_article_fingerprint("  BREAKING: Historic Accord Signed  ", "global gazette", canonical)
    assert len(fp1) == 64
    assert fp1 == fp2  # Normalized case-insensitivity on title & publisher


def test_is_duplicate_article(db_session):
    art = _create_mock_article(1, batch_state="active")
    db_session.add(art)
    db_session.commit()

    # Exact canonical URL duplicate
    assert is_duplicate_article(db_session, art.canonical_url, "fake_fingerprint_123") is True

    # Same fingerprint duplicate
    assert is_duplicate_article(db_session, "https://different.com/unique-url", art.article_fingerprint) is True

    # Truly unique article
    assert is_duplicate_article(db_session, "https://example.com/unique-url-999", "unique_fingerprint_999") is False

    # Check against ArticleHistory record
    hist_canonical = "https://example.com/archived-historical-url"
    hist_fg = compute_article_fingerprint("Old Historical Title", "Archive Source", hist_canonical)
    hist = ArticleHistory(
        article_id=999,
        canonical_url=hist_canonical,
        fingerprint=hist_fg,
        title="Old Historical Title",
        source_name="Archive Source",
    )
    db_session.add(hist)
    db_session.commit()

    assert is_duplicate_article(db_session, hist_canonical, "new_fingerprint_123") is True
    assert is_duplicate_article(db_session, "https://example.com/other", hist_fg) is True


# ---------------------------------------------------------------------------
# 2. Ingestion Manager Lifecycle & Status Tests
# ---------------------------------------------------------------------------
def test_manager_get_status_empty(db_session):
    manager = IngestionManager()
    status = manager.get_status(db_session=db_session)
    assert status["active_count"] == 0
    assert status["reserve_count"] == 0
    assert status["consumed_count"] == 0
    assert status["is_refilling"] is False
    assert status["can_rotate"] is False


def test_manager_get_status_with_batches(db_session):
    for i in range(50):
        db_session.add(_create_mock_article(i, batch_state="active", batch_id="batch_active_1"))
    for i in range(50, 100):
        db_session.add(_create_mock_article(i, batch_state="reserve", batch_id="batch_reserve_1"))
    db_session.commit()

    manager = IngestionManager()
    status = manager.get_status(db_session=db_session)
    assert status["active_count"] == 50
    assert status["reserve_count"] == 50
    assert status["consumed_count"] == 0
    assert status["can_rotate"] is True


# ---------------------------------------------------------------------------
# 3. Batch Rotation Tests
# ---------------------------------------------------------------------------
def test_rotate_batch_success(db_session):
    # Setup 50 active and 50 reserve
    for i in range(50):
        db_session.add(_create_mock_article(i, batch_state="active", batch_id="batch_act_1"))
    for i in range(50, 100):
        db_session.add(_create_mock_article(i, batch_state="reserve", batch_id="batch_res_1"))
    db_session.commit()

    manager = IngestionManager()
    with patch.object(manager, "_run_refill_worker"):
        result = manager.rotate_batch(db_session=db_session)
        assert result["status"] == "rotated"
        assert result["rotated_count"] == 50
        assert len(result["items"]) == 50
        assert len(result["articles"]) == 50

        # Verify old 50 are now consumed
        consumed_count = db_session.query(Article).filter(Article.batch_state == "consumed").count()
        assert consumed_count == 50

        # Verify new 50 are now active
        active_count = db_session.query(Article).filter(Article.batch_state == "active").count()
        assert active_count == 50

        # Verify ArticleHistory records were recorded
        history_count = db_session.query(ArticleHistory).count()
        assert history_count == 50


def test_rotate_batch_shortage_preserves_active(db_session):
    # Setup 50 active but only 20 reserve (shortage)
    for i in range(50):
        db_session.add(_create_mock_article(i, batch_state="active", batch_id="batch_act_1"))
    for i in range(50, 70):
        db_session.add(_create_mock_article(i, batch_state="reserve", batch_id="batch_res_1"))
    db_session.commit()

    manager = IngestionManager()
    with patch.object(manager, "_run_refill_worker"):
        result = manager.rotate_batch(db_session=db_session)
        # Should not rotate partially
        assert result["status"] == "refill_in_progress"
        assert result["ready_count"] == 20
        assert result["rotated_count"] == 0

        # Active articles must remain untouched
        active_count = db_session.query(Article).filter(Article.batch_state == "active").count()
        assert active_count == 50
        consumed_count = db_session.query(Article).filter(Article.batch_state == "consumed").count()
        assert consumed_count == 0


# ---------------------------------------------------------------------------
# 4. Payload Pruning & History Persistence Tests
# ---------------------------------------------------------------------------
def test_cleanup_consumed_payloads(db_session):
    manager = IngestionManager()
    # Add 10 consumed articles
    for i in range(10):
        art = _create_mock_article(i, batch_state="consumed", batch_id="batch_old")
        db_session.add(art)
    db_session.commit()

    # Clean up with max_retained=5
    manager._cleanup_consumed_payloads(db_session, max_retained=5)
    db_session.commit()

    consumed = db_session.query(Article).filter(Article.batch_state == "consumed").all()
    assert len(consumed) == 5

    # Check that deleted articles had their history records preserved
    history = db_session.query(ArticleHistory).all()
    assert len(history) == 5


# ---------------------------------------------------------------------------
# 5. Background Refill Concurrency Lock Test
# ---------------------------------------------------------------------------
def test_refill_concurrency_lock():
    manager = IngestionManager()
    manager._is_refilling = True
    result = manager.trigger_refill()
    assert result["status"] == "already_refilling"


# ---------------------------------------------------------------------------
# 6. REST API Endpoints Integration Tests
# ---------------------------------------------------------------------------
def test_api_batch_status_endpoint():
    with patch("app.routers.ingest.ingestion_manager.get_status") as mock_status:
        mock_status.return_value = {
            "active_count": 50,
            "reserve_count": 50,
            "consumed_count": 0,
            "history_count": 0,
            "target_batch_size": 50,
            "is_refilling": False,
            "can_rotate": True,
            "refill_progress": {"target": 50, "ready": 50, "status": "idle", "message": "Ready"}
        }

        with TestClient(app) as client:
            res = client.get("/api/ingest/batch-status")
            assert res.status_code == 200
            data = res.json()
            assert data["active_count"] == 50
            assert data["reserve_count"] == 50
            assert data["is_refilling"] is False
            assert data["can_rotate"] is True


def test_api_batch_rotate_endpoint():
    with patch("app.routers.ingest.ingestion_manager.rotate_batch") as mock_rotate:
        mock_rotate.return_value = {
            "status": "rotated",
            "message": "Activated 50 fresh articles",
            "batch_id": "batch_test_123",
            "active_batch_id": "batch_test_123",
            "rotated_count": 50,
            "count": 50,
            "active_count": 50,
            "reserve_count": 50,
            "ready_count": 50,
            "reserve_remaining": 50,
            "items": [],
            "articles": [],
            "is_refilling": True
        }

        with TestClient(app) as client:
            res = client.post("/api/ingest/rotate")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "rotated"
            assert data["rotated_count"] == 50
            assert data["active_count"] == 50
            assert data["active_batch_id"] == "batch_test_123"


def test_rotate_batch_cors_headers():
    with TestClient(app) as client:
        res = client.post("/api/ingest/rotate", headers={"Origin": "http://localhost:3000"})
        assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_rotate_batch_duplicate_fingerprint_resilience(db_session):
    # Setup 2 active articles with duplicate fingerprint
    art1 = _create_mock_article(1, batch_state="active", batch_id="batch_act_1")
    art2 = _create_mock_article(2, batch_state="active", batch_id="batch_act_1")
    art2.article_fingerprint = art1.article_fingerprint  # Force duplicate fingerprint
    db_session.add(art1)
    db_session.add(art2)

    for i in range(10, 60):
        db_session.add(_create_mock_article(i, batch_state="reserve", batch_id="batch_res_1"))
    db_session.commit()

    manager = IngestionManager()
    with patch.object(manager, "_run_refill_worker"):
        res = manager.rotate_batch(db_session=db_session)
        assert res["status"] == "rotated"
        assert res["rotated_count"] == 50
        # Ensure only 1 history record created for duplicate fingerprint without crashing
        hist = db_session.query(ArticleHistory).filter(ArticleHistory.fingerprint == art1.article_fingerprint).all()
        assert len(hist) == 1
