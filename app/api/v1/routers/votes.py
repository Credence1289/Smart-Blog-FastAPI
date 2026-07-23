from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models import models
from app.db.session import get_db
from app.schemas.upvote_schema import VoteCreate
from app.core.gate import current_user
from app.models.models import User, Post, Vote

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/posts/{post_id}/vote")
async def vote_post(
        post_id: int,
        new_vote: VoteCreate,
        db: AsyncSession = Depends(get_db),
        current: dict = Depends(current_user)
):
    user = current["user"]

    result = await db.execute(
        select(models.Post).where(models.Post.post_id == post_id)
    )
    existing_post = result.scalar_one_or_none()

    if not existing_post:
        logger.info("Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db.execute(
        select(models.Vote).where(
            models.Vote.post_id == post_id,
            models.Vote.user_id == user.user_id
        )
    )
    existing_vote = result.scalar_one_or_none()

    # CREATES NEW VOTE
    if not existing_vote:
        db.add(models.Vote(
            user_id=user.user_id,
            post_id=post_id,
            vote=new_vote.vote
        ))
        await db.commit()
        return {"Message": f"Vote created for {post_id}"}

    # IF ALREADY VOTED THEN IT REMOVES THE VOTE
    if existing_vote.vote == new_vote.vote:
        await db.delete(existing_vote)
        await db.commit()
        return {"Message": f"Vote removed for {post_id}"}

    existing_vote.vote = new_vote.vote
    await db.commit()
    return {"Message": f"Vote updated for {post_id}"}


@router.get("/posts/{post_id}/vote")
async def get_votes(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current: dict = Depends(current_user)
):
    result = await db.execute(
        select(models.Post).where(models.Post.post_id == post_id)
    )
    existing_post = result.scalar_one_or_none()

    if not existing_post:
        logger.info("Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db.execute(
        select(func.count())
        .select_from(models.Vote)
        .where(models.Vote.post_id == post_id, models.Vote.vote == 1)
    )
    upvotes = result.scalar_one()

    result = await db.execute(
        select(func.count())
        .select_from(models.Vote)
        .where(models.Vote.post_id == post_id, models.Vote.vote == -1)
    )
    downvotes = result.scalar_one()

    return {
        "upvotes": upvotes,
        "downvotes": downvotes
    }