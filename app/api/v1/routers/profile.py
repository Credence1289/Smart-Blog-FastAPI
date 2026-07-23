from fastapi import FastAPI, Depends, HTTPException,status,APIRouter
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

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
async def create_profile(
    profile: ProfileIn,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    result = await db.execute(
        select(models.Profile)
        .where(models.Profile.user_id == user.user_id)
    )
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already created."
        )

    new_profile = models.Profile(
        user_id=user.user_id,
        bio=profile.bio,
    )

    db.add(new_profile)
    await db.commit()
    result = await db.execute(
        select(models.Profile)
        .options(selectinload(models.Profile.user))
        .where(models.Profile.profile_id == new_profile.profile_id)
    )
    new_profile = result.scalar_one()

    return new_profile


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    result = await db.execute(
        select(models.Profile)
        .where(models.Profile.user_id == user.user_id)
    )
    profile = result.scalar_one_or_none()

    if not user or not profile:
        logger.info(f"Profile not found for {user.user_id}")
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


@router.get("/{username}", response_model=ProfileOut)
async def get_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
    current:dict = Depends(current_user),
):
    result = await db.execute(
        select(models.Profile)
        .options(selectinload(models.Profile.user))
        .join(models.User, models.Profile.user_id == models.User.user_id)
        .where(models.User.username == username)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return profile

@router.patch("/me", response_model=ProfileOut)
async def update_profile(
    profile: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(current_user),
):
    user = current["user"]

    result = await db.execute(
        select(models.Profile).where(models.Profile.user_id == user.user_id)
    )
    existing_profile = result.scalar_one_or_none()

    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    if profile.bio is not None:
        existing_profile.bio = profile.bio

    await db.commit()

    result = await db.execute(
        select(models.Profile)
        .options(selectinload(models.Profile.user))
        .where(models.Profile.profile_id == existing_profile.profile_id)
    )
    existing_profile = result.scalar_one()

    return existing_profile