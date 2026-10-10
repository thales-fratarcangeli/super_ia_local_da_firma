from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI()
DB = {}
_next = [1]

class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    body: str = ""

@app.post("/notes", status_code=201)
def create(n: NoteIn):
    i = _next[0]
    _next[0] += 1
    DB[i] = {"id": i, **n.model_dump()}
    return DB[i]

@app.get("/notes")
def list_notes(q: Optional[str] = None):
    return [v for k, v in sorted(DB.items()) if q is None or q.lower() in v["title"].lower()]

@app.get("/notes/{id}")
def get(id: int):
    if id not in DB:
        raise HTTPException(404, "not found")
    return DB[id]

@app.put("/notes/{id}")
def put(id: int, n: NoteIn):
    if id not in DB:
        raise HTTPException(404, "not found")
    DB[id] = {"id": id, **n.model_dump()}
    return DB[id]

@app.delete("/notes/{id}", status_code=204)
def delete(id: int):
    if id not in DB:
        raise HTTPException(404, "not found")
    del DB[id]
    return Response(status_code=204)
