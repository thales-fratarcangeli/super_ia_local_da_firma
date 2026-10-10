from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional

app = FastAPI()

ITEMS = list(range(1, 36))

@app.get("/items")
def get_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    min: Optional[int] = None
):
    if min is not None:
        filtered = [item for item in ITEMS if item >= min]
    else:
        filtered = ITEMS

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
