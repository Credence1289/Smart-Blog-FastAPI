from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import logging

from app.models import models
from app.db.session import get_db
from app.schemas.upvote_schema import VoteCreate
from app.core.gate import current_user
from app.models.models import User, Post, Vote

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/posts/{post_id}/vote")
def vote_post(
        post_id:int,
        new_vote: VoteCreate,
        db: Session = Depends(get_db),
        current:dict = Depends(current_user)
):
    existing_post = (
        db.query(models.Post).filter(models.Post.post_id == post_id).first()
    )
    if not existing_post:
        logger.info("Post not found")
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    existing_vote = (
        db.query(models.Vote)
        .filter_by(
            post_id = post_id,
            user_id = current["user"].user_id
        )
        .first()
    )
    #CREATES NEW VOTE
    if not existing_vote:
        db.add(Vote(
            user_id = current["user"].user_id,
            post_id = post_id,
            vote=new_vote.vote
        ))
        db.commit()
        return {"Message": f"Vote created for {post_id}"}

    #IF ALREADY VOTED THEN IT REMOVES THE VOTE
    if existing_vote.vote == new_vote.vote:
        db.delete(existing_vote)
        db.commit()
        return {"Message": f"Vote removed for {post_id}"}


    existing_vote.vote = new_vote.vote
    db.commit()
    return {"Message": f"Vote updated for {post_id}"}


@router.get("/posts/{post_id}/vote")
def get_votes(
        post_id: int,
        db: Session = Depends(get_db),
        current:dict=Depends(current_user)
):

    existing_post = (
        db.query(models.Post).filter(models.Post.post_id == post_id).first()
    )
    if not existing_post:
        logger.info("Post not found")
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    upvotes = db.query(Vote).filter_by(
        post_id=post_id,
        vote=1
    ).count()

    downvotes = db.query(Vote).filter_by(
        post_id=post_id,
        vote=-1
    ).count()

    return {
        "upvotes": upvotes,
        "downvotes": downvotes
    }

