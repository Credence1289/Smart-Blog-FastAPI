from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from app.core.logger import set_logger

set_logger()

from app.api.v1.api import sb_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:

    logger.info("Starting Smart Blog API.....")

    app = FastAPI(
        title="Smart Blog API",
        description="Smart Blogging",
        docs_url="/api/v1/docs",
        version="v1",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/api/v1/docs")
        
    app.include_router(sb_router, prefix="/api/v1", tags=["v1"])

    return app

app = create_app()



