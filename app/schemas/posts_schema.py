from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    content_type : str
    title : str
    post : str

class PostShow(BaseModel):
    post_id : int
    username: str
    content_type: str
    title: str
    post: str
    created_at: datetime = Field(default_factory=datetime.now)

class PostUpdate(BaseModel):
    content_type: Optional[str] = None
    title: Optional[str] = None
    post: Optional[str] = None