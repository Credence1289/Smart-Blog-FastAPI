from pydantic import BaseModel,Field,ConfigDict,field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class CommentsIn(BaseModel):
    comment:str = Field(
        min_length=1,
        max_length=500
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

class CommentsOut(BaseModel):
    user_id:int
    post_id:int
    comments_id:UUID
    comment: str
    created_at:datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class CommentsUpdate(BaseModel):
    comment: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value):
        if not value:
            raise ValueError("Comment cannot be empty.")
        return value