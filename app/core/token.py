from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
import uuid
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY   #python3  -> import secrets -> secret.token_hex(16)
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRY_MIN = settings.ACCESS_TOKEN_EXPIRY_MIN

def create_token(
        user_id : int,
        role : str,
        expiry : timedelta = None,
        refresh : bool = False
):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + (
            expiry if expiry is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRY_MIN)
        ),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

    return token

def decode_token(token : str)->dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed", exc_info=exc)
        return None
