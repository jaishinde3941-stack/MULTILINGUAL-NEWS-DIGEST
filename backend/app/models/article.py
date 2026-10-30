from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String(1000), unique=True, index=True, nullable=False)
    source_name = Column(String(100), index=True, nullable=False) # e.g. Le Monde, El País, DW
    
    # Original language & text
    original_language = Column(String(50), index=True, nullable=False)
    original_title = Column(Text, nullable=False)
    original_content = Column(Text, nullable=False)
    original_summary = Column(Text, nullable=True) # Distilled summary in original source language
    
    # LLM processed fields (Strictly English headline and 80-120 word summary - no full translation)
    english_title = Column(Text, nullable=False)
    english_summary = Column(Text, nullable=False)
    english_content = Column(Text, nullable=False)
    
    # Categorization & metadata tags
    region = Column(String(100), index=True, nullable=False)
    subregion = Column(String(100), index=True, nullable=True)
    field = Column(String(100), index=True, nullable=False) # e.g. Technology & AI, Geopolitics
    keywords = Column(JSON, default=list) # List of extracted key phrases
    
    # Scoring & trending
    trending = Column(Boolean, default=False, index=True)
    trending_score = Column(Float, default=0.5)
    
    # Quality & processing tracking
    processing_status = Column(String(30), default="completed", index=True) # completed, pending, failed, flagged
    processing_error = Column(Text, nullable=True)
    summary_word_count = Column(Integer, default=0)
    
    image_url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bookmarks = relationship("Bookmark", back_populates="article", cascade="all, delete-orphan")
