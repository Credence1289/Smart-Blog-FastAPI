from typing import List
from fastapi import APIRouter,HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import logging
from uuid import UUID
import json

from app.rate_limit.limiter import limiter
from app.rate_limit.config import *
from app.cache.redis_client import redis_client
from app.cache.keys import *
from app.schemas.pagination_schema import PaginateCommentsOut
from app.models import models
from app.db.session import get_db
from app.schemas.comments_schema import CommentsIn, CommentsOut, CommentsUpdate
from app.core.gate import current_user
from app.models.models import User, Post, Vote, Comment
from app.dependencies.pagination import pagination_param
from app.utils.pagination import paginate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/posts/{post_id}/comments", response_model=CommentsOut)
@limiter.limit(CREATE_LIMIT)
async def create_comment(
    request: Request,
    post_id:int,
    comment: CommentsIn,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):
    user = current["user"]

    result = await db.execute(
        select(models.Post)
        .where(models.Post.post_id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        logger.info("Post does not exist")
        raise HTTPException(
            status_code=404,
            detail="Post does not exist"
        )
    new_comment = models.Comment(
        comment=comment.comment,
        post_id=post_id,
        user_id=user.user_id,
    )

    db.add(new_comment)
    await db.commit()

    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.user))
        .where(models.Comment.comments_id == new_comment.comments_id)
    )
    new_comment = result.scalar_one()

    logger.info(
        f"User {current['user'].user_id} commented on post {post_id}"
    )

    return new_comment

@router.get("/posts/{post_id}/comments",response_model=PaginateCommentsOut)
@limiter.limit(GENERAL_LIMIT)
async def read_comments(
    request: Request,
    post_id: int,
    pagination=Depends(pagination_param),
    db: AsyncSession = Depends(get_db)
):

    key = comments_key(
        post_id,
        pagination["page"],
        pagination["size"]
    )
    cached_comments = await redis_client.get(key)

    if cached_comments:
        print("Cache Hit")
        return json.loads(cached_comments)

    result = await db.execute(
       select(models.Post)
       .where(models.Post.post_id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    stmt = (
        select(models.Comment)
        .options(selectinload(models.Comment.user))
        .where(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at.desc())
    )
    # result = await db.execute(stmt)
    # comments = result.scalars().all()
    result = await paginate(
        db=db,
        stmt=stmt,
        page=pagination["page"],
        size=pagination["size"],
        key="comments",
    )
    comments_out =  PaginateCommentsOut.model_validate(result)
    await redis_client.set(
        key,
        comments_out.model_dump_json(),
        ex=600
    )

    logger.info(
        f"Fetched comments for post {post_id}"
    )

    return result 

@router.patch("/comments/{comments_id}", response_model=CommentsOut)
@limiter.limit(UPDATE_LIMIT)
async def update_comment(
    request: Request,
    comments_id: UUID,
    comment_data: CommentsUpdate,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):
    user = current["user"]

    result = await db.execute(
        select(models.Comment)
        .where(models.Comment.comments_id == comments_id)
    )

    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update comment"
        )

    update_data = comment_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(comment, field, value)

    await db.commit()

    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.user))
        .where(models.Comment.comments_id == comments_id)
    )
    up_comment = result.scalar_one()
    await redis_client.delete(comment_key(comments_id))

    logger.info(
        f"Comment {comments_id} updated"
    )

    return up_comment

@router.delete("/comments/{comments_id}")
@limiter.limit(DELETE_LIMIT)
async def delete_comment(
    request: Request,
    comments_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):
    user = current["user"]

    result = await db.execute(
        select(models.Comment)
        .where(models.Comment.comments_id == comments_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    await db.delete(comment)
    await db.commit()
    
    await redis_client.delete(comment_key(comments_id))
    logger.info(
        f"Comment {comments_id} deleted"
    )

    return {
        "message": "Comment deleted successfully"
    }