from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class Booking(BaseModel):
    guest: str = Field(min_length=1)
    start: date
    end: date
    nights: Optional[int] = None

    @model_validator(mode="after")
    def check(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        self.nights = (self.end - self.start).days
        return self
