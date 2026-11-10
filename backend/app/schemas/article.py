from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_url: str
    source_name: str
    original_language: str
    original_title: str
    original_content: str
    original_summary: Optional[str] = None
    english_title: str
    english_summary: str
    english_content: str
    region: str
    subregion: Optional[str] = None
    field: str
    keywords: List[str] = []
    trending: bool = False
    trending_score: float = 0.5
    processing_status: Optional[str] = "completed"
    processing_error: Optional[str] = None
    summary_word_count: Optional[int] = 0
    batch_id: Optional[str] = None
    batch_state: Optional[str] = "active"
    canonical_url: Optional[str] = None
    image_url: Optional[str] = None
    published_at: datetime
    created_at: datetime
    match_score: Optional[float] = None
    is_bookmarked: Optional[bool] = False

class ArticleListResponse(BaseModel):
    total: int
    items: List[ArticleResponse]

class FilterMetaResponse(BaseModel):
    regions: List[str]
    languages: List[str]
    fields: List[str]

class IngestResult(BaseModel):
    scraped_count: int
    processed_count: int
    skipped_count: int
    errors: List[str] = []

class BatchStatusResponse(BaseModel):
    active_count: int
    reserve_count: int
    consumed_count: int
    target_batch_size: int = 50
    active_batch_id: Optional[str] = None
    is_refilling: bool
    refill_progress: Optional[dict] = None
    can_rotate: bool
    message: Optional[str] = None

class BatchRotateResponse(BaseModel):
    status: str
    message: str
    batch_id: Optional[str] = None
    active_batch_id: Optional[str] = None
    rotated_count: int = 0
    count: int = 0
    active_count: int = 0
    reserve_count: int = 0
    reserve_remaining: int = 0
    ready_count: int = 0
    items: List[ArticleResponse] = []
    articles: List[ArticleResponse] = []
    is_refilling: bool = False
