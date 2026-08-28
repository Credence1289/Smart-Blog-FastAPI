from fastapi import FastAPI, Depends, HTTPException,status,APIRouter, Request
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
import json

from app.rate_limit.limiter import limiter
from app.rate_limit.config import *
from app.cache.redis_client import redis_client
from app.cache.keys import *
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


@router.post("/me",response_model=ProfileOut,status_code=status.HTTP_201_CREATED)
@limiter.limit(CREATE_LIMIT)
async def create_profile(
    request: Request,
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
        .options(
            selectinload(models.Profile.user),
            selectinload(models.Profile.profile_pic),
        )
        .where(models.Profile.profile_id == new_profile.profile_id)
    )
    new_profile = result.scalar_one()

    return new_profile


@router.get("/me", response_model=ProfileOut)
@limiter.limit(GENERAL_LIMIT)
async def get_my_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    key = profile_key(user.user_id)

    cached_profile = await redis_client.get(key)

    if cached_profile:
        print("Cache Hit")
        return json.loads(cached_profile)
    
    result = await db.execute(
        select(models.Profile)
        .options(
            selectinload(models.Profile.user),
            selectinload(models.Profile.profile_pic),
        )
        .where(models.Profile.user_id == user.user_id)
    )
    profile = result.scalar_one_or_none()
    cache_profile = ProfileOut.model_validate(profile)
    if not user or not profile:
        logger.info(f"Profile not found for {user.user_id}")
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    await redis_client.set(
        key,
        cache_profile.model_dump_json(),
    )
        
    return profile


@router.get("/{username}", response_model=ProfileOut)
@limiter.limit(REGISTER_LIMIT)
async def get_profile(
    request: Request,
    username: str,
    db: AsyncSession = Depends(get_db),
    current:dict = Depends(current_user),
):
    
    result = await db.execute(
        select(models.Profile)
        .options(
            selectinload(models.Profile.user),
            selectinload(models.Profile.profile_pic),
        )
        .join(models.User, models.Profile.user_id == models.User.user_id)
        .where(models.User.username == username)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return profile

@router.patch("/me", response_model=ProfileOut)
@limiter.limit(UPDATE_LIMIT)
async def update_profile(
    request: Request,
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
        .options(
            selectinload(models.Profile.user),
            selectinload(models.Profile.profile_pic),
        )
        .where(models.Profile.profile_id == existing_profile.profile_id)
    )
    existing_profile = result.scalar_one()

    await redis_client.delete(profile_key(user.user_id))
    
    return existing_profile