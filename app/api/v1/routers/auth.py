from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.schemas.refresh_token_schema import RefreshTokenReq
from app.schemas.users_schema import UserIn, UserOut
from app.db.session import get_db
from app.core.hashing import hash_password, verify_password
from app.core.token import create_token, decode_token
from app.core.gate import current_user
from app.models import models
from datetime import timedelta
from app.core.config import settings


router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register")
def register_user(
    user: UserIn,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )
    if existing_user:
        logger.info("User already exists")
        raise HTTPException(status_code=400, detail="User already exists")

    username_exists = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )
    if username_exists:
        logger.info("Username already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("User successfully register")
    return {"Message" : f"User successfully created!!"}


@router.post("/login")
def login_user(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Authentication failed for username%s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = create_token(user_id=user.user_id, role="user")

    refresh_token = create_token(
        user_id=user.user_id,
        role="user",
        refresh = True,
        expiry = timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    )
    logger.info(f"User successfully logged in ")

    return {
        "username": user.username,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/user/refresh")
def refresh_access_token(
    data: RefreshTokenReq
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

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }