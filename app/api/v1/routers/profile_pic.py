import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
async def upsert_profile_pic(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user),
):
    """
    Uploads (or replaces) the current user's profile picture.

    Order of operations, same as we discussed:
    1. Save the NEW file to disk first.
    2. Update/create the DB row to point at the new file.
    3. Only then delete the OLD file, once the new one is safely recorded.
    """
    user = current["user"]
    profile = await _get_profile_or_404(db, user.user_id)

    result = await db.execute(
        select(models.ProfilePic).where(models.ProfilePic.profile_id == profile.profile_id)
    )
    existing_pic = result.scalar_one_or_none()

    # Step 1: save the new file (validates type/size, writes to disk)
    saved_as, folder, size = await save_profile_pic(file)

    # Remember the old file's location BEFORE we overwrite the row
    old_folder = existing_pic.folder if existing_pic else None
    old_saved_as = existing_pic.saved_as if existing_pic else None

    # Step 2: update or create the DB row to point at the new file
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

    # Step 3: only now delete the old file, since the DB is confirmed updated
    if old_saved_as:
        delete_profile_pic_file(old_folder, old_saved_as)

    return pic


@router.get("/me", response_model=ProfilePicOut)
async def get_my_profile_pic(
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
async def delete_my_profile_pic(
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
async def get_profile_pic_file(
    pic_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint that serves the actual image bytes -- this is the URL
    you'd put in an <img src="..."> tag. No auth required: profile pictures
    are meant to be visible on any user's public profile.
    """
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
