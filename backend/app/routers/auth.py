from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account with default profile."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    hashed_pw = hash_password(user_in.password)
    new_user = User(
        email=user_in.email.lower(),
        hashed_password=hashed_pw,
        full_name=user_in.full_name
    )
    db.add(new_user)
    db.flush()

    # Create associated profile
    new_profile = Profile(
        user_id=new_user.id,
        completed_onboarding=False,
        interest_weights={},
        preferred_languages=[],
        preferred_regions=[],
        preferred_fields=[],
        quiz_answers={}
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"user_id": new_user.id, "email": new_user.email})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        completed_onboarding=False
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate existing user credentials and return JWT bearer token."""
    user = db.query(User).filter(User.email == login_data.email.lower()).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    completed = user.profile.completed_onboarding if user.profile else False
    access_token = create_access_token(data={"user_id": user.id, "email": user.email})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        completed_onboarding=completed
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return currently authenticated user details."""
    completed = current_user.profile.completed_onboarding if current_user.profile else False
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        completed_onboarding=completed
    )
