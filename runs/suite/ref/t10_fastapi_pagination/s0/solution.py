from typing import Optional
from fastapi import FastAPI, Query

app = FastAPI()
DATA = list(range(1, 36))

@app.get("/items")
def items(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50), min: Optional[int] = None):
    data = [x for x in DATA if min is None or x >= min]
    s = (page - 1) * page_size
    return {"items": data[s:s + page_size], "total": len(data), "page": page, "page_size": page_size}
