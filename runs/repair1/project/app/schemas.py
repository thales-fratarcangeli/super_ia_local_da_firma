from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "member"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

class ProjectCreate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str

class TaskStatusEnum(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
