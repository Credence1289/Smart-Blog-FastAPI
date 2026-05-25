from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


from app.schema.users_schemas import UserIn, UserOut
from app.db.session import get_db
from app.core.hashing import hash_password, verify_password
from app.core.token import create_access_token, decode_token
from app.core.gate import current_user
from app.models import models

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(
    user: UserIn,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(db_models.User)
        .filter(db_models.User.email == user.email)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    username_exists = (
        db.query(db_models.User)
        .filter(db_models.User.username == user.username)
        .first()
    )
    if username_exists:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = db_models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login_user(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(db_models.User)
        .filter(db_models.User.username == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = create_access_token(user_id=user.user_id, role="user")
    return {"access_token": access_token, "token_type": "bearer"}
