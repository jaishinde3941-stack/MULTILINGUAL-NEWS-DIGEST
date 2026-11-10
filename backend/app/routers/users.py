from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.profile import ProfileResponse
from app.auth.deps import get_current_user, get_optional_current_user

router = APIRouter(tags=["Users & Profile"])

@router.get("/api/users/profile", response_model=ProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile information."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, completed_onboarding=True)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        completed_onboarding=True,
        interest_weights={},
        preferred_languages=profile.preferred_languages or [],
        preferred_regions=profile.preferred_regions or [],
        preferred_fields=profile.preferred_fields or [],
        quiz_answers={},
        updated_at=profile.updated_at
    )

@router.get("/api/users/{user_id}/profile", response_model=ProfileResponse)
def get_user_profile_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Retrieve profile by user ID."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        profile = Profile(user_id=user_id, completed_onboarding=True)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        completed_onboarding=True,
        interest_weights={},
        preferred_languages=profile.preferred_languages or [],
        preferred_regions=profile.preferred_regions or [],
        preferred_fields=profile.preferred_fields or [],
        quiz_answers={},
        updated_at=profile.updated_at
    )
