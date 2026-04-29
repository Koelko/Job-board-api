from pydantic import BaseModel, Field
from typing import Optional


class EmployerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=255)

class EmployerCreate(EmployerBase):
    password_hash: str = Field(..., min_length=5, max_length=255)

class EmployerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    password_hash: Optional[str] = Field(None, min_length=5, max_length=255)

class EmployerResponse(EmployerBase):
    id: int 
    vacancy_count: int 
    rating: Optional[float] = None
    class Config:
        from_attributes = True