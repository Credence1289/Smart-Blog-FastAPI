from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from app.core.logger import set_logger
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

set_logger()

from app.rate_limit.limiter import limiter
from app.db.dbengine import AsyncEngine
from app.cache.redis_client import redis_client
from app.api.v1.api import sb_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app:FastAPI):
    #---------Startup----------
    logger.info("Starting Smart Blog API...")
    try:
        await redis_client.ping()
        logger.info("Redis Connected")
    except Exception as e:
        logger.error(f"Redis Connection Failed: {e}")

    yield           # app runs here, serving requests

    #---------Shutdown----------
    logger.info("Shutting down Smart Blog API....")
    await AsyncEngine.dispose()     # closes the DB connection pool
    await redis_client.aclose()    # closes the redis connection
 
def create_app() -> FastAPI:

    app = FastAPI(
        title="Smart Blog API",
        description="Smart Blogging",
        docs_url="/api/v1/docs",
        version="v1",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://localhost:3000","http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.state.limiter = limiter   #SlowAPI limiter object
    
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler
    )

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/api/v1/docs")
        
    app.include_router(sb_router, prefix="/api/v1", tags=["v1"])

    return app

app = create_app()


