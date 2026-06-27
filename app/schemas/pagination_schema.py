from pydantic import BaseModel
from typing import List

from app.schemas.posts_schema import PostShow
from app.schemas.comments_schema import CommentsOut

class PaginatePostOut(BaseModel):
    posts : List[PostShow]
    total:int
    offset:int
    limit:int
    has_more:bool

class PaginateCommentsOut(BaseModel):
    comments:List[CommentsOut]
    total:int
    offset:int
    limit:int
    has_more:bool