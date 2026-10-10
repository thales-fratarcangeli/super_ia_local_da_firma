def paginate(items, page=1, page_size=10):
    if page < 1 or not 1 <= page_size <= 50:
        raise ValueError("invalid")
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "total": len(items), "page": page, "page_size": page_size}
