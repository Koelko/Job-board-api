from pydantic import BaseModel, Field
from typing import Optional

class SeekerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None)
    email: str = Field(..., min_length=1, max_length=255)

class SeekerCreate(SeekerBase):
    password: str = Field(..., min_length=5, max_length=255)

class SeekerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=5, max_length=255)

class SeekerResponse(SeekerBase):
    id: int 
    class Config:
        from_attributes = True