from sqlalchemy.orm import Query

def paginate(query:Query,page:int,size:int, key:str = "items"):

    total = query.count()

    offset = (page - 1) * size

    items = (
        query
        .offset(offset)
        .limit(size)
        .all()
    )

    return {
        key: items,
        "total": total,
        "offset": offset,
        "limit": size,
        "has_more": offset + size < total
    }