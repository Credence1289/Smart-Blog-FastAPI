import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rate_limit.limiter import limiter
from app.rate_limit.config import *
from app.db.session import get_db
from app.core.gate import current_user
from app.models import models
from app.schemas.profile_pic_schema import ProfilePicOut
from app.utils.image_utils import (
    save_profile_pic,
    delete_profile_pic_file,
    UPLOAD_ROOT,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_profile_or_404(db: AsyncSession, user_id: int) -> models.Profile:
    result = await db.execute(
        select(models.Profile).where(models.Profile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create a profile before uploading a profile picture.",
        )
    return profile


@router.put("/me", response_model=ProfilePicOut, status_code=status.HTTP_200_OK)
@limiter.limit(UPDATE_LIMIT)
async def upsert_profile_pic(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):

    user = current["user"]
    profile = await _get_profile_or_404(db, user.user_id)

    result = await db.execute(
        select(models.ProfilePic).where(models.ProfilePic.profile_id == profile.profile_id)
    )
    existing_pic = result.scalar_one_or_none()

    #save the new file
    saved_as, folder, size = await save_profile_pic(file)

    old_folder = existing_pic.folder if existing_pic else None
    old_saved_as = existing_pic.saved_as if existing_pic else None

    # update or create the DB row to point at the new file
    if existing_pic:
        existing_pic.original_name = file.filename
        existing_pic.saved_as = saved_as
        existing_pic.folder = folder
        existing_pic.size = size
        pic = existing_pic
    else:
        pic = models.ProfilePic(
            user_id=user.user_id,
            profile_id=profile.profile_id,
            original_name=file.filename,
            saved_as=saved_as,
            folder=folder,
            size=size,
        )
        db.add(pic)

    await db.commit()
    await db.refresh(pic)

    #only now delete the old file, since the DB is confirmed updated
    if old_saved_as:
        delete_profile_pic_file(old_folder, old_saved_as)

    return pic


@router.get("/me", response_model=ProfilePicOut)
@limiter.limit(GENERAL_LIMIT)
async def get_my_profile_pic(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    result = await db.execute(
        select(models.ProfilePic).where(models.ProfilePic.user_id == user.user_id)
    )
    pic = result.scalar_one_or_none()

    if not pic:
        raise HTTPException(status_code=404, detail="No profile picture set.")

    return pic


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(DELETE_LIMIT)
async def delete_my_profile_pic(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    user = current["user"]

    result = await db.execute(
        select(models.ProfilePic).where(models.ProfilePic.user_id == user.user_id)
    )
    pic = result.scalar_one_or_none()

    if not pic:
        raise HTTPException(status_code=404, detail="No profile picture to delete.")

    folder, saved_as = pic.folder, pic.saved_as

    await db.delete(pic)
    await db.commit()

    delete_profile_pic_file(folder, saved_as)
    return None


@router.get("/file/{pic_id}")
@limiter.limit(GENERAL_LIMIT)
async def get_profile_pic_file(
    request: Request,
    pic_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.ProfilePic).where(models.ProfilePic.pic_id == pic_id)
    )
    pic = result.scalar_one_or_none()

    if not pic:
        raise HTTPException(status_code=404, detail="Profile picture not found.")

    file_path = (UPLOAD_ROOT / pic.folder / pic.saved_as).resolve()
    upload_root = UPLOAD_ROOT.resolve()

    if upload_root not in file_path.parents or not file_path.exists():
        raise HTTPException(status_code=404, detail="Profile picture file missing.")

    return FileResponse(path=file_path, filename=pic.original_name)
