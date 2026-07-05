from pydantic import BaseModel, Field, ConfigDict
from typing import Optional,List
from datetime import datetime

class PostCreate(BaseModel):
    content_type : str
    title : str
    post : str

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

class PostShow(BaseModel):
    post_id : int
    username: str
    content_type: str
    title: str
    post: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class PostUpdate(BaseModel):
    content_type: Optional[str] = None
    title: Optional[str] = None
    post: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

class TrendingPostOut(BaseModel):
    score: int
    post: PostShow

    model_config = {
        "from_attributes": True
    }