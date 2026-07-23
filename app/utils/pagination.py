from sqlalchemy.orm import Query
from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession

async def paginate(
        db: AsyncSession,
        stmt: Select,
        page:int,
        size:int,
        key:str = "items"
):
    offset = (page - 1) * size

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    paged_stmt = stmt.offset(offset).limit(size)
    result = await db.execute(paged_stmt)
    items = result.scalars().all()

    return {
        key: items,
        "total": total,
        "offset": offset,
        "limit": size,
        "has_more": offset + size < total
    }