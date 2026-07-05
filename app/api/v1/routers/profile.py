from fastapi import FastAPI, Depends, HTTPException,status,APIRouter
import logging
from sqlalchemy.orm import Session

from app.schemas.profile_schema import ProfileIn, ProfileOut,ProfileUpdate
from app.db.session import get_db
from app.core.gate import current_user
from app.models.models import Profile
from app.models import models
from app.models.models import User, Profile, Post
from uuid import UUID
from datetime import timedelta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/me",response_model=ProfileOut,status_code=status.HTTP_201_CREATED,)
def create_profile(
    profile: ProfileIn,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    existing_profile = (
        db.query(Profile)
        .filter(Profile.user_id == user.user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists."
        )

    new_profile = models.Profile(
        user_id=user.user_id,
        bio=profile.bio,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "bio": new_profile.bio,
        "posts": user.posts,
    }


@router.get("/me", response_model=ProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current["user"].user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    return {
        "name": current["user"].name,
        "username": current["user"].username,
        "email": current["user"].email,
        "bio": profile.bio,
        "posts": current["user"].posts,
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
        db.query(models.Profile)
        .filter(Profile.user_id == current["user"].user_id)
        .first()
    )

    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )

    if profile.post is not None:
        existing_profile.post = profile.post

    db.commit()
    db.refresh(existing_profile)

    return {
        "name": current["user"].name,
        "username": current["user"].username,
        "email": current["user"].email,
        "bio": existing_profile.bio,
        "posts": current["user"].posts,
    }