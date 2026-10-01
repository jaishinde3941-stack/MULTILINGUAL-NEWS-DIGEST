from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.quiz import QuizListResponse
from app.schemas.profile import OnboardingSubmission, ProfileResponse
from app.services.quiz_data import get_quiz_response, calculate_interest_graph
from app.auth.deps import get_current_user, get_optional_current_user

router = APIRouter(tags=["Users & Onboarding"])

@router.get("/api/onboarding/questions", response_model=QuizListResponse)
def get_onboarding_questions():
    """Retrieve the full 15-question onboarding questionnaire."""
    return get_quiz_response()

@router.post("/api/onboarding/submit", response_model=ProfileResponse)
def submit_onboarding(
    submission: OnboardingSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process 15-question onboarding answers, generate interest graph weights,
    and persist user preferences.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    graph_data = calculate_interest_graph(submission.answers)
    
    # Store raw answers dictionary
    answers_dict = {str(a.question_id): a.selected_option_ids for a in submission.answers}
    
    profile.interest_weights = graph_data["interest_weights"]
    profile.preferred_languages = graph_data["preferred_languages"]
    profile.preferred_regions = graph_data["preferred_regions"]
    profile.preferred_fields = graph_data["preferred_fields"]
    profile.quiz_answers = answers_dict
    profile.completed_onboarding = True

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        completed_onboarding=profile.completed_onboarding,
        interest_weights=profile.interest_weights or {},
        preferred_languages=profile.preferred_languages or [],
        preferred_regions=profile.preferred_regions or [],
        preferred_fields=profile.preferred_fields or [],
        quiz_answers=profile.quiz_answers or {},
        updated_at=profile.updated_at
    )

@router.post("/api/users/{user_id}/profile", response_model=ProfileResponse)
def save_user_profile_by_id(
    user_id: int,
    submission: OnboardingSubmission,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Save onboarding answers for user id (Milestone 2 specification).
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.add(profile)

    graph_data = calculate_interest_graph(submission.answers)
    answers_dict = {str(a.question_id): a.selected_option_ids for a in submission.answers}

    profile.interest_weights = graph_data["interest_weights"]
    profile.preferred_languages = graph_data["preferred_languages"]
    profile.preferred_regions = graph_data["preferred_regions"]
    profile.preferred_fields = graph_data["preferred_fields"]
    profile.quiz_answers = answers_dict
    profile.completed_onboarding = True

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        completed_onboarding=profile.completed_onboarding,
        interest_weights=profile.interest_weights or {},
        preferred_languages=profile.preferred_languages or [],
        preferred_regions=profile.preferred_regions or [],
        preferred_fields=profile.preferred_fields or [],
        quiz_answers=profile.quiz_answers or {},
        updated_at=profile.updated_at
    )

@router.get("/api/users/profile", response_model=ProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's interest graph profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id, completed_onboarding=False)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        completed_onboarding=profile.completed_onboarding,
        interest_weights=profile.interest_weights or {},
        preferred_languages=profile.preferred_languages or [],
        preferred_regions=profile.preferred_regions or [],
        preferred_fields=profile.preferred_fields or [],
        quiz_answers=profile.quiz_answers or {},
        updated_at=profile.updated_at
    )
