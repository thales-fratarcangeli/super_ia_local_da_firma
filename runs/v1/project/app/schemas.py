from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime
from app.models import User, Project, Task

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["member", "admin"] = "member"

class UserResponse(BaseModel):
    id: int
    username: str
    role: Literal["member", "admin"]
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]

class ProjectCreate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    model_config = ConfigDict(from_attributes=True)

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Literal["todo", "doing", "done"] = "todo"

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: Literal["todo", "doing", "done"]
    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    model_config = ConfigDict(from_attributes=True)
