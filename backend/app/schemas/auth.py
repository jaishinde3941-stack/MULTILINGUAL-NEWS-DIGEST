from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: Optional[str] = None
    completed_onboarding: bool = False

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    completed_onboarding: bool = False
