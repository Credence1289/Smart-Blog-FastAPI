from contextlib import asynccontextmanager
from redis.asyncio import Redis
from app.core.config import settings

def create_redis_client():
    r = Redis(
        host="settings.REDIS_HOST",
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    return r

redis_client = create_redis_client()