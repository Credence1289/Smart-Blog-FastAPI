from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.posts import router as posts_router
from app.api.v1.routers.votes import router as votes_router
from app.api.v1.routers.comments import router as comments_router
from app.api.v1.routers.health_check import router as health_router
from app.api.v1.routers.profile import router as profile_router
version = "v1"

sb_router = APIRouter()

sb_router.include_router(auth_router)
sb_router.include_router(posts_router)
sb_router.include_router(votes_router)
sb_router.include_router(comments_router)
sb_router.include_router(profile_router)
sb_router.include_router(health_router)