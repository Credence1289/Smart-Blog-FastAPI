from fastapi import FastAPI, Depends, HTTPException,status
import logging
from sqlalchemy.orm import Session

from app.schemas.users_schema import ProfileIn, ProfileOut,ProfileUpdate
from app.db.session import get_db
from app.core.gate import current_user
from app.models.models import Profile
from app.models import models
from app.models.models import User, Profile, Post
from uuid import UUID
from datetime import timedelta

router = APIRouter()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("/me",response_model=ProfileOut,status_code=status.HTTP_201_CREATED,)
def create_profile(
    profile: ProfileIn,
    db: Session = Depends(get_db),
    current: User = Depends(current_user),
):
    existing_profile = (
        db.query(Profile)
        .filter(Profile.user_id == current.user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists."
        )

    new_profile = Profile(
        user_id=current.user_id,
        bio=profile.bio,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "name": current.name,
        "username": current.username,
        "email": current.email,
        "bio": new_profile.bio,
        "posts": current.posts,
    }


@router.get("/me", response_model=ProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current: User = Depends(current_user),
):
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current.user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    return {
        "name": current.name,
        "username": current.username,
        "email": current.email,
        "bio": profile.bio,
        "posts": current.posts,
    }


@router.get("/{username}", response_model=ProfileOut)
def get_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if not user.profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    return {
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "bio": user.profile.bio,
        "posts": user.posts,
    }


@router.patch("/me", response_model=ProfileOut)
def update_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(current_user),
):
    existing_profile = (
        db.query(Profile)
        .filter(Profile.user_id == current.user_id)
        .first()
    )

    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    if profile.bio is not None:
        existing_profile.bio = profile.bio

    db.commit()
    db.refresh(existing_profile)

    return {
        "name": current.name,
        "username": current.username,
        "email": current.email,
        "bio": existing_profile.bio,
        "posts": current.posts,
    }