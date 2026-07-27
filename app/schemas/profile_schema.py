from pydantic import BaseModel, EmailStr,ConfigDict
from typing import List,Optional

from app.schemas.profile_pic_schema import ProfilePicOut
from app.schemas.posts_schema import PostShow

class ProfileIn(BaseModel):
    bio: str | None = None


class ProfileUpdate(BaseModel):
    bio: str | None = None


class ProfileOut(BaseModel):
    profile_pic: Optional[ProfilePicOut] = None
    name: str
    username: str
    email: str
    bio: str | None

    model_config = ConfigDict(
        from_attributes=True
    )