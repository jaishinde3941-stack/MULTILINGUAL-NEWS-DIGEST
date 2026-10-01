from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional, Any
from datetime import datetime

class OnboardingAnswer(BaseModel):
    question_id: int
    selected_option_ids: List[str]

class OnboardingSubmission(BaseModel):
    answers: List[OnboardingAnswer]

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    completed_onboarding: bool
    interest_weights: Dict[str, float]
    preferred_languages: List[str]
    preferred_regions: List[str]
    preferred_fields: List[str]
    quiz_answers: Dict[str, Any]
    updated_at: Optional[datetime] = None
