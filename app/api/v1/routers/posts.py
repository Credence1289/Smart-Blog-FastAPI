from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, Query
from sqlalchemy import func, case #lets you call sqlfucntion #if else
from typing import Optional
import logging

from app.schemas.posts_schema import PostCreate, PostShow,PostUpdate,TrendingPostOut
from app.schemas.users_schema import UserIn, UserOut
from app.schemas.pagination_schema import PaginatePostOut
from app.db.session import get_db
from app.core.hashing import hash_password, verify_password
from app.core.token import create_token, decode_token
from app.core.gate import current_user
from app.models.models import User, Post,Comment,Vote
from app.models import models
from app.dependencies.pagination import pagination_param
from app.utils.pagination import paginate

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/posts", response_model=PostShow)
def create_post(
     post: PostCreate,
     db: Session = Depends(get_db),
     current: dict = Depends(current_user)
):
    new_post = models.Post(
        user_id=current["user"].user_id,
        content_type=post.content_type,
        title=post.title,
        post=post.post,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    logger.info(
        "New post created",
        extra={
            "user_id": new_post.user_id,
            "post_id": new_post.post_id,
            "content_type": new_post.content_type,
            "title": new_post.title,
        }
    )
    return new_post

# Current user's posts
@router.get("/posts/me", response_model=PaginatePostOut)
def show_my_posts(
        pagination=Depends(pagination_param),
        db: Session = Depends(get_db),
        current: dict = Depends(current_user)
):
    posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == current["user"].user_id)
        .order_by(models.Post.created_at.desc())
        # .all()
    )
    logger.info(f"Posts fetched by {current['user'].user_id}")

    # return posts
    return paginate(
        query=posts,
        page=pagination["page"],
        size=pagination["size"],
        key="posts"
    )

@router.get("/posts/{post_id}", response_model=PostShow)
def show_post(
        post_id: int,
        db:Session = Depends(get_db),
        current:dict = Depends(current_user),
):
    post = (
        db.query(models.Post)
        .filter(models.Post.post_id == post_id)
        .first()
    )
    if not post:
        logger.info("Post not found")
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    logger.info(f"Post fetched by {current['user'].username}")

    return post

@router.get("/posts", response_model=PaginatePostOut)
def show_all_posts(
    content_type: str = "all",
    pagination=Depends(pagination_param),
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):

    query = db.query(models.Post).join(models.User)

    if content_type.lower() != "all":
        query = query.filter(
            models.Post.content_type == content_type
        )

    query = query.order_by(models.Post.created_at.desc())

    logger.info(f"Posts fetched by {current['user'].username} ")

    return paginate(
        query=query,
        page=pagination["page"],
        size=pagination["size"],
        key="posts"
    )


@router.patch("/posts/{post_id}")
def update_post(
    post_id:int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):
    existing_post = (
        db.query(models.Post)
        .filter(models.Post.post_id == post_id)
        .first()
    )
    if not existing_post:
        logger.warning("Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    if existing_post.user_id != current["user"].user_id:
        logger.warning("Invalid user")
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    # update_data = post.model_dump(exclude_unset=True)
    #
    # for field, value in update_data.items(): #removes fields the user didn't send.
    #     setattr(existing_post, field, value) #Set the attribute whose name is stored in field

    if post.title is not None:
        existing_post.title = post.title

    if post.post is not None:
        existing_post.post = post.post

    if post.content_type is not None:
        existing_post.content_type = post.content_type

    db.commit()
    db.refresh(existing_post)
    logger.info("Post is successfully updated")

    return {"Message": "Post Updated "}


@router.delete("/posts")
def delete_all_posts(
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):
    db.query(models.Post).filter(models.Post.user_id == current["user"].user_id).delete()
    db.commit()
    logger.info("Posts successfully deleted")

    return {"Message": "Posts successfully deleted"}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user)
):
    post = (
        db.query(models.Post)
        .filter(models.Post.post_id == post_id)
        .first()
    )
    if not post:
        logger.error("Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current["user"].user_id:
        logger.warning(f"Invalid user")
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()
    logger.info(f"Post is successfully deleted")

    return {"Message": "Post Deleted"}


@router.get("/trending",response_model=list[TrendingPostOut] )
def get_trending_posts(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    trending_posts = (db.query(Post,
            (
                func.sum( #computes the score
                    case(
                        (Vote.vote == 1, 1),
                        (Vote.vote == -1, -1),
                        else_=0,
                    )
                )
                + func.count(Comment.comments_id) * 2
            ).label("score"),
        )
        .outerjoin(Vote, Vote.post_id == Post.post_id)
        .outerjoin(Comment, Comment.post_id == Post.post_id)
        .group_by(Post.post_id)
        .order_by(func.coalesce(func.sum( #tells how to sort rows
            case(
                (Vote.vote == 1, 1),
                (Vote.vote == -1, -1),
                else_=0,
            )
        ), 0) + func.count(Comment.comments_id) * 2)
        .limit(limit)
        .all()
    )

    return [
        {
            "post": post,
            "score": score,
        }
        for post, score in trending_posts
    ]