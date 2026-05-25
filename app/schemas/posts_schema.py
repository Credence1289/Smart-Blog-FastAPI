from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    username : Optional[str] = None
    post_id : Optional[int] = None
    content_type : str
    title : str
    post : str

class PostShow(BaseModel):
    post_id : Optional[int] = None
    username: str
    content_type: str
    title: str
    post: str
    created_at: datetime = Field(default_factory=datetime.now)