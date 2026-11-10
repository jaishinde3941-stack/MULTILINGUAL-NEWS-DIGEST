from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base

class ArticleHistory(Base):
    """
    Lightweight history record for deduplication.
    Persists canonical URLs and fingerprints even after obsolete article bodies
    are cleaned up from the main articles table.
    """
    __tablename__ = "article_history"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, nullable=True, index=True)
    canonical_url = Column(String(1000), nullable=False, index=True)
    fingerprint = Column(String(64), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    source_name = Column(String(100), nullable=False, index=True)
    consumed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
