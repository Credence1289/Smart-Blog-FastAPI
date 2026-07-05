from typing import List

from fastapi import APIRouter,HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from uuid import UUID

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
def create_comment(post_id:int,comment: CommentsIn, db: Session = Depends(get_db), current: dict = Depends(current_user)):
    user = current["user"]
    post = (
        db.query(models.Post)
        .filter(models.Post.post_id == post_id)
        .first()
    )
    if not post:
        logger.info("Post does not exist")
        raise HTTPException(
            status_code=404,
            detail="Post does not exist"
        )
    new_comment = Comment(
        comment=comment.comment,
        post_id=post_id,
        user_id=user.user_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    logger.info(
        f"User {current['user'].user_id} commented on post {post_id}"
    )

    return CommentsOut(
        user_id=new_comment.user_id,
        post_id=new_comment.post_id,
        username=user.username,
        comments_id=new_comment.comments_id,
        comment=new_comment.comment,
        created_at=new_comment.created_at,
    )

@router.get("/posts/{post_id}/comments",response_model=PaginateCommentsOut)
def read_comments(
    post_id: int,
    pagination=Depends(pagination_param),
    db: Session = Depends(get_db)
):

    post = (
        db.query(Post)
        .filter(Post.post_id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        # .all()
    )

    logger.info(
        f"Fetched comments for post {post_id}"
    )

    return paginate(
        query=comments,
        page=pagination["page"],
        size=pagination["size"],
        key="comments"

    )

@router.patch("/comments/{comments_id}")
def update_comment(
    comments_id: UUID,
    comment_data: CommentsUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):

    comment = (
        db.query(Comment)
        .filter(Comment.comments_id == comments_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != current["user"].user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    update_data = comment_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(comment, field, value)

    db.commit()
    db.refresh(comment)

    logger.info(
        f"Comment {comments_id} updated"
    )

    return {
        "message": "Comment updated successfully"
    }

@router.delete("/comments/{comments_id}")
def delete_comment(
    comments_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):

    comment = (
        db.query(Comment)
        .filter(Comment.comments_id == comments_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != current["user"].user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    db.delete(comment)
    db.commit()

    logger.info(
        f"Comment {comments_id} deleted"
    )

    return {
        "message": "Comment deleted successfully"
    }