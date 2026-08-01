import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status


UPLOAD_ROOT = Path("uploads")
PROFILE_PIC_SUBFOLDER = "profile_pics"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image.jpg", "image/png"}
EXT_BY_CONTENT_TYPE = {"image/jpeg": ".jpg", "image/png": ".png"}
MAX_PROFILE_PIC_SIZE = 10 * 1024 * 1024


def profile_pic_dir() -> Path:
    target_dir = UPLOAD_ROOT / PROFILE_PIC_SUBFOLDER
    target_dir.mkdir(parents=True, exist_ok=True) # creates it the first time it's needed
    return target_dir

async def save_profile_pic(file: UploadFile) -> tuple[str, str, int]:

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: jpeg, png.",
        )

    target_dir = profile_pic_dir()
    ext = EXT_BY_CONTENT_TYPE[file.content_type]
    unique_name = f"{uuid.uuid4().hex}{ext}" # random unique filename, keeps extension
    file_path = target_dir / unique_name

    size = 0
    # version's read/write are await-able, meaning they yield control back to the event loop instead of blocking it.

    async with aiofiles.open(file_path, "wb") as buffer:
        # this is the walrus operator (:=), which assigns and checks a value in one line.
        # It reads the file in 1MB chunks instead of await file.read() all at once
        while chunk := await file.read(1024 * 1024):  # 1MB at a time
            size += len(chunk)
            if size > MAX_PROFILE_PIC_SIZE:
                await buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File too large. Max size is 5MB.",
                )
            await buffer.write(chunk)

    return unique_name, PROFILE_PIC_SUBFOLDER, size


def delete_profile_pic_file(folder: str, saved_as: str) -> None:

    file_path = (UPLOAD_ROOT / folder / saved_as).resolve()
    upload_root = UPLOAD_ROOT.resolve()

    if upload_root not in file_path.parents:
        return

    if file_path.exists() and file_path.is_file():
        file_path.unlink()
