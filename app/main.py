from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import sb_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Blog API",
        description="Smart Blogging",
        docs_url="/api/v1/docs",
        version="v1",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(sb_router, prefix="/api/v1", tags=["v1"])

    return app

app = create_app()



