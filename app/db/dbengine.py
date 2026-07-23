from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = str(settings.DATABASE_URL)

if not DATABASE_URL:
    logger.critical("DATABASE_URL environment variable not set")
    raise RuntimeError("DATABASE_URL is not set")

AsyncEngine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": "require"},
    echo = False
)