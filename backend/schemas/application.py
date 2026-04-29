from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ApplicationBase(BaseModel):
    status: Optional[str] = Field(None)

class ApplicationCreate(ApplicationBase):
    vacancy_id: int = Field(..., gt=0)
    resume_id: int = Field(..., gt=0)

class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None)

class ApplicationResponse(ApplicationBase,):
    id: int
    application_date: Optional[date] = Field(None)
    class Config:
        feom_attributes = True