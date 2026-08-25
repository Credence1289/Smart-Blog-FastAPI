from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()

@router.get("/smartblog_health")
async def health_check(
        db:AsyncSession = Depends(get_db)
):
    try:
        await db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "SmartBlog",
            "database": "connected",

        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "failed",
                "database": "unavailable"
            }
        )

