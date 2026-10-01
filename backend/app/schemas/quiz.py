from pydantic import BaseModel
from typing import List, Dict, Optional

class QuizOption(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    # Weights mapped to dimensions: e.g. {"region:Europe": 1.0, "field:Technology & AI": 0.8}
    weight_map: Dict[str, float]

class QuizQuestion(BaseModel):
    id: int
    dimension: str # "region", "field", "language"
    title: str
    subtitle: str
    is_multi_select: bool = False
    options: List[QuizOption]

class QuizListResponse(BaseModel):
    total_questions: int
    questions: List[QuizQuestion]
