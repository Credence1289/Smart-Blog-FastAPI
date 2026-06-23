from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime

class CommentsIn(BaseModel):
    comment:str = Field(
        min_length=1,
        max_length=500
    )

class CommentsOut(BaseModel):
    user_id:int
    post_id:int
    comments_id:UUID
    comment: str
    created_at:datetime = Field(default_factory=datetime.now)

    model_config = {
        "from_attributes": True
    }

class CommentsUpdate(BaseModel):
    comment:str = Field(
        min_length=1,
        max_length=500
    )