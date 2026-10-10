from fastapi import FastAPI, Depends, HTTPException, Header, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel
from pydantic import Field
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from typing import Optional, List, Annotated
from enum import Enum as PyEnum

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")

# Inicialização do banco de dados
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de usuário
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="member")
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")

# Modelo de projeto
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

# Modelo de tarefa
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tasks")
    title = Column(String)
    description = Column(String)
    status = Column(String, default="todo")
    owner = relationship("User", back_populates="tasks")

# Criação das tabelas
Base.metadata.create_all(bind=engine)

# Inicialização da aplicação
app = FastAPI()

# Dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependência para obter o token
def get_token(authorization: Annotated[str, Header(...)]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    return token

# Dependência para obter o usuário autenticado
def get_current_user(token: str = Depends(get_token), db: SessionLocal = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Modelo de usuário para registro
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "member"

# Modelo de usuário para resposta
class UserResponse(BaseModel):
    id: int
    username: str
    role: str

# Modelo de projeto para criação
class ProjectCreate(BaseModel):
    name: str

# Modelo de projeto para resposta
class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

# Modelo de tarefa para criação
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

# Modelo de tarefa para resposta
class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str

# Modelo de resposta para listagem
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int

# Enum para status da tarefa
class TaskStatusEnum(str, PyEnum):
    todo = "todo"
    doing = "doing"
    done = "done"

# Rota de registro
@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    if len(user.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    if user.role not in ["member", "admin"]:
        raise HTTPException(status_code=422, detail="Invalid role")
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = User(username=user.username, password=hashed_password.decode("utf-8"), role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Rota de login
@app.post("/auth/login")
def login(username: str, password: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(minutes=60)
        },
        JWT_SECRET,
        algorithm="HS256"
    )
    return {"access_token": token, "token_type": "bearer"}

# Rota para criar projeto
@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    if not project.name:
        raise HTTPException(status_code=422, detail="Name is required")
    db_project = Project(name=project.name, owner_id=user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Rota para listar projetos
@app.get("/projects", response_model=PaginatedResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    skip = (page - 1) * page_size
    limit = page_size
    if user.role == "member":
        projects = db.query(Project).filter(Project.owner_id == user.id).offset(skip).limit(limit).all()
    else:
        projects = db.query(Project).offset(skip).limit(limit).all()
    total = db.query(Project).count()
    return {
        "items": [{"id": p.id, "name": p.name, "owner_id": p.owner_id} for p in projects],
        "total": total,
        "page": page,
        "page_size": page_size
    }

# Rota para obter projeto por ID
@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role == "member" and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return project

# Rota para deletar projeto
@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role == "member" and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(project)
    db.commit()

# Rota para criar tarefa
@app.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    project_id: int,
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role == "member" and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not task.title:
        raise HTTPException(status_code=422, detail="Title is required")
    if task.status not in ["todo", "doing", "done"]:
        raise HTTPException(status_code=422, detail="Invalid status")
    db_task = Task(
        project_id=project_id,
        title=task.title,
        description=task.description,
        status=task.status
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Rota para listar tarefas de um projeto
@app.get("/projects/{project_id}/tasks", response_model=PaginatedResponse)
def list_tasks(
    project_id: int,
    status: Optional[TaskStatusEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if user.role == "member" and project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status.value)
    skip = (page - 1) * page_size
    limit = page_size
    tasks = query.offset(skip).limit(limit).all()
    total = query.count()
    return {
        "items": [{"id": t.id, "title": t.title, "description": t.description, "status": t.status} for t in tasks],
        "total": total,
        "page": page,
        "page_size": page_size
    }

# Rota para atualizar tarefa
@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: dict,
    user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user.role == "member" and db_task.project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in task.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

# Rota para deletar tarefa
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user.role == "member" and db_task.project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(db_task)
    db.commit()
