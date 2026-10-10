from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["todo", "doing", "done"]


class RegisterIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=6)
    role: Literal["member", "admin"] = "member"


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProjectIn(BaseModel):
    name: str = Field(min_length=1)


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    owner_id: int


class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: Status = "todo"


class TaskPatch(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    status: Optional[Status] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
