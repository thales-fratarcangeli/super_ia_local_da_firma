from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import schemas
from app.auth import create_token, current_user, hash_password, verify_password
from app.database import Base, engine, get_db
from app.models import Project, Task, User

Base.metadata.create_all(engine)
app = FastAPI()


def paginate(db: Session, stmt, model, page: int, page_size: int, schema):
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(model.id).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [schema.model_validate(r) for r in rows], "total": total, "page": page, "page_size": page_size}


def get_project(db: Session, user: User, project_id: int) -> Project:
    p = db.get(Project, project_id)
    if p is None:
        raise HTTPException(404, "Project not found")
    if p.owner_id != user.id and user.role != "admin":
        raise HTTPException(403, "Forbidden")
    return p


def get_task(db: Session, user: User, task_id: int) -> Task:
    t = db.get(Task, task_id)
    if t is None:
        raise HTTPException(404, "Task not found")
    get_project(db, user, t.project_id)
    return t


@app.post("/auth/register", status_code=201, response_model=schemas.UserOut)
def register(body: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == body.username)):
        raise HTTPException(409, "Username already exists")
    u = User(username=body.username, password_hash=hash_password(body.password), role=body.role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.username == body.username))
    if u is None or not verify_password(body.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(u.id), "token_type": "bearer"}


@app.post("/projects", status_code=201, response_model=schemas.ProjectOut)
def create_project(body: schemas.ProjectIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = Project(name=body.name, owner_id=user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/projects")
def list_projects(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50),
                  user: User = Depends(current_user), db: Session = Depends(get_db)):
    stmt = select(Project)
    if user.role != "admin":
        stmt = stmt.where(Project.owner_id == user.id)
    return paginate(db, stmt, Project, page, page_size, schemas.ProjectOut)


@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def read_project(project_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_project(db, user, project_id)


@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(get_project(db, user, project_id))
    db.commit()
    return Response(status_code=204)


@app.post("/projects/{project_id}/tasks", status_code=201, response_model=schemas.TaskOut)
def create_task(project_id: int, body: schemas.TaskIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_project(db, user, project_id)
    t = Task(project_id=project_id, **body.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@app.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int, status: Optional[schemas.Status] = None, page: int = Query(1, ge=1),
               page_size: int = Query(10, ge=1, le=50), user: User = Depends(current_user),
               db: Session = Depends(get_db)):
    get_project(db, user, project_id)
    stmt = select(Task).where(Task.project_id == project_id)
    if status:
        stmt = stmt.where(Task.status == status)
    return paginate(db, stmt, Task, page, page_size, schemas.TaskOut)


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def patch_task(task_id: int, body: schemas.TaskPatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    t = get_task(db, user, task_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(get_task(db, user, task_id))
    db.commit()
    return Response(status_code=204)
