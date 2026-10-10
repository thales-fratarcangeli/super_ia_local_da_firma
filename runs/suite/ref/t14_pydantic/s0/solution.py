import re
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class SignUp(BaseModel):
    username: str
    password: str = Field(min_length=6)
    age: Optional[int] = Field(default=None, ge=13, le=120)
    role: Literal["member", "admin"] = "member"

    @field_validator("username")
    @classmethod
    def check_username(cls, v):
        if not 3 <= len(v) <= 20 or not re.fullmatch(r"[A-Za-z0-9_]+", v):
            raise ValueError("invalid username")
        return v.lower()
