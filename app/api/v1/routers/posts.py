from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,delete, case,desc #lets you call sqlfucntion #if else,
from sqlalchemy.orm import selectinload
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
from app.utils.email_utils import send_email,send_first_post_congrats_email

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/posts", response_model=PostShow)
async def create_post(
     post: PostCreate,
     background_tasks : BackgroundTasks,
     db: AsyncSession = Depends(get_db),
     current: dict = Depends(current_user)
):
    user =  current["user"]

    result = await db.execute(
        select(func.count(models.Post.post_id))
        .where(models.Post.user_id == user.user_id)
    )
    is_first_post = result.scalar_one() == 0

    new_post = models.Post(
        content_type=post.content_type,
        title=post.title,
        post=post.post,
        user_id=user.user_id,
    )
    db.add(new_post)
    await db.commit()
    # await db.refresh(new_post, attribute_names="user") or
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.user))
        .where(models.Post.post_id == new_post.post_id)
    )
    new_post = result.scalar_one()
    #is more consistent with your codebase's existing style and less error-prone
    # if PostShow grows more nested relationships later (comments, votes, etc.)
    # — you just add more .options(selectinload(...)) to one query instead of
    # remembering to refresh(attribute_names=[...]) for each one.

    logger.info(
        "New post created",
        extra={
            "user_id": user.user_id,
            "post_id": new_post.post_id,
            "username": user.username,
            "content_type": new_post.content_type,
            "title": new_post.title,
        }
    )
    if is_first_post:
        background_tasks.add_task(
            send_first_post_congrats_email, user.email, user.name, new_post.title
        )
    return new_post

# Current user's posts
@router.get("/posts/me", response_model=PaginatePostOut)
async def show_my_posts(
        pagination=Depends(pagination_param),
        db: AsyncSession = Depends(get_db),
        current: dict = Depends(current_user)
):
    user = current["user"]

    #You expect multiple rows (a list of posts)
    stmt = (
        select(models.Post)
        .options(selectinload(models.Post.user))
        .where(models.Post.user_id == user.user_id)
        .order_by(models.Post.created_at.desc())
    )
    result = await db.execute(stmt)
    post = result.scalars().all()

    logger.info(f"Posts fetched by {user.username}")

    # return posts
    return await paginate(
        db=db,
        stmt=stmt,
        page=pagination["page"],
        size=pagination["size"],
        key="posts"
    )

@router.get("/posts/{post_id}", response_model=PostShow)
async def show_post(
        post_id: int,
        db:AsyncSession = Depends(get_db),
):
    #You expect a single row — fetching by primary key or unique field
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.user))
        .where(models.Post.post_id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        logger.info("Post not found")
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    logger.info(f"Post fetched by user")

    return post

@router.get("/posts", response_model=PaginatePostOut)
async def show_all_posts(
    content_type: str = "all",
    pagination=Depends(pagination_param),
    db: AsyncSession = Depends(get_db),
):

    stmt = (
        select(models.Post)
        .options(selectinload(models.Post.user))
        .order_by(models.Post.created_at.desc())
    )

    if content_type != "all":
        stmt = stmt.where(models.Post.content_type == content_type)

    result = await db.execute(stmt)
    post = result.scalars().all()

    logger.info(f"Posts fetched by a user ")

    return await paginate(
        db=db,
        stmt=stmt,
        page=pagination["page"],
        size=pagination["size"],
        key="posts"
    )


@router.patch("/posts/{post_id}", response_model=PostShow)
async def update_post(
    post_id:int,
    post: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.user))
        .where(models.Post.post_id == post_id)
    )
    existing_post = result.scalar_one_or_none()

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

    await db.commit()
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.user))
        .where(models.Post.post_id == existing_post.post_id)
    )
    existing_post = result.scalar_one()
    logger.info("Post is successfully updated")

    return existing_post


@router.delete("/posts")
async def delete_all_posts(
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):
    user = current["user"]

    await db.execute(
        delete(models.Post).where(models.Post.user_id == user.user_id)
    )
    await db.commit()
    logger.info("Posts successfully deleted")

    return {"Message": "Posts successfully deleted"}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(current_user)
):

    result = await db.execute(
        select(models.Post).where(models.Post.post_id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        logger.error("Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current["user"].user_id:
        logger.warning(f"Invalid user")
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await db.delete(post)
    await db.commit()
    logger.info(f"Post is successfully deleted")

    return {"Message": "Post Deleted"}


@router.get("/trending",response_model=list[TrendingPostOut] )
async def get_trending_posts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    #vote_score
    vote_scores = (
        select(
            Vote.post_id.label("post_id"),
            func.sum(
                case(
                    (Vote.vote == 1, 1),
                    (Vote.vote == -1, -1),
                    else_=0,
                )
            ).label("vote_score"),
        )
        .group_by(Vote.post_id)
        .subquery()
    )
    # comment_score
    comment_counts = (
        select(
            Comment.post_id.label("post_id"),
            func.count(Comment.comments_id).label("comment_count"),
        )
        .group_by(Comment.post_id)
        .subquery()
    )

    score_expr = (
            func.coalesce(vote_scores.c.vote_score, 0)
            + func.coalesce(comment_counts.c.comment_count, 0) * 2
    )

    stmt = (
        select(
            Post,
            score_expr.label("score")
        )
        .options(selectinload(Post.user))
        .outerjoin(
            vote_scores,
            vote_scores.c.post_id == Post.post_id
        )
        .outerjoin(
            comment_counts,
            comment_counts.c.post_id == Post.post_id
        )
        .order_by(desc(score_expr))
        .limit(limit)
    )

    result = await db.execute(stmt)
    trending_posts = result.all()

    return [
        {
            "post": post,
            "score": score,
        }
        for post, score in trending_posts
    ]