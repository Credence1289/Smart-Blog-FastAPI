from fastapi import APIRouter, HTTPException, Depends, status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import logging
from sqlalchemy import select

from app.schemas.token_schema import RefreshTokenIn, TokenOut, AccessTokenOut, ResetPasswordIn,ForgotPasswordIn
from app.schemas.users_schema import UserIn, UserOut
from app.db.session import get_db
from app.core.hashing import hash_password, verify_password
from app.core.token import create_token, decode_token
from app.core.gate import current_user
from app.models import models
from datetime import timedelta
from app.core.config import settings
from app.utils.email_utils import send_email, send_welcome_email,password_reset_link,send_first_post_congrats_email

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register", response_model = UserOut,status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserIn,
    background_tasks:BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.info("User is already registered")
        raise HTTPException(
            status_code=400,
            detail="User is already registered",
        )
    result = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    username_exist = result.scalar_one_or_none()
    if username_exist:
        logger.info("Username is already taken")
        raise HTTPException(
            status_code=400,
            detail="Username is already taken",
        )
    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info("User registered")
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    return new_user


@router.post("/login", response_model=TokenOut)
async def login_user(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(
        select(models.User).where(models.User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Authentication failed for username %s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = create_token(user_id=user.user_id, role="user")

    refresh_token = create_token(
        user_id=user.user_id,
        role="user",
        refresh = True,
        expiry = timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    )
    logger.info(f"User successfully logged in %s", user.username)

    return TokenOut(
        username=user.username,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )

@router.post("/user/refresh", response_model=AccessTokenOut)
def refresh_access_token(
    data: RefreshTokenIn,
):
    payload = decode_token(data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("refresh") is not True:
        raise HTTPException(
            status_code=401,
            detail="Not a refresh token"
        )

    new_access_token = create_token(
        user_id=payload["user_id"],
        role=payload["role"]
    )

    return AccessTokenOut(
        access_token=new_access_token,
        token_type="Bearer"
    )


@router.post("/forgot_password")
async def forgot_password(
        data:ForgotPasswordIn,
        background_tasks:BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user:
        reset_token = create_token(
            user_id=user.user_id,
            role="password-reset",
            expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
        )
        background_tasks.add_task(password_reset_link, user.email, reset_token.token)
        logger.info(f"Password reset requested for {user.user_id}")

    return {"message" : "Reset link has been sent"}

@router.post("/reset_password", response_model=TokenOut)
async def reset_password(
        data: ResetPasswordIn,
        db:AsyncSession = Depends(get_db)
):
    payload = decode_token(data.token)

    if payload is None or payload.get("role") != "password-reset":
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    result = await db.execute(
        select(models.User).where(models.User.user_id == payload["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    user.password = hash_password(data.new_password)
    await db.commit()
    await db.refresh(user)

    logger.info(f"Password reset completed for {payload.user_id}")

    return {"message": "Password reset successful"}
