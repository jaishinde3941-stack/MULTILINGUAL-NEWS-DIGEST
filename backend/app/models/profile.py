from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Interest weights map tag/category/region to float score (e.g. {"region_europe": 0.85, "field_tech": 0.9})
    interest_weights = Column(JSON, default=dict)
    
    # Extracted preference tags
    preferred_languages = Column(JSON, default=list)
    preferred_regions = Column(JSON, default=list)
    preferred_fields = Column(JSON, default=list)
    
    # Stored 15-question answers for audit/re-evaluation
    quiz_answers = Column(JSON, default=dict)
    
    completed_onboarding = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
