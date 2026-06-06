from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from app.core.token import decode_token
from app.db.session import get_db
from app.models import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    payload = decode_token(token)
    if payload is None:
        logger.warning("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get user_id and role from payload
    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if role == "user":
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            logger.warning("User not found : user_id=%s", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"user": user, "role": role, "payload": payload}

    else:
        logger.warning("Invalid role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role"
        )