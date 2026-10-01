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
