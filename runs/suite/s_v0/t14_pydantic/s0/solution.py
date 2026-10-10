from pydantic import BaseModel, field_validator
from typing import Literal, Optional

class SignUp(BaseModel):
    username: str
    password: str
    age: Optional[int] = None
    role: Literal["member", "admin"] = "member"

    @field_validator('username')
    def validate_username(cls, value: str) -> str:
        if not 3 <= len(value) <= 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not value.isalnum() and '_' not in value:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return value.lower()

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters')
        return value

    @field_validator('age')
    def validate_age(cls, value: Optional[int]) -> Optional[int]:
        if value is not None:
            if not 13 <= value <= 120:
                raise ValueError('Age must be between 13 and 120')
        return value
