from pydantic import BaseModel, Field
from typing import Optional

class VacancyListBase(BaseModel):
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    list_name: Optional[str] = Field(None, min_length=1, max_length=255)

class VacancyListCreate(VacancyListBase):
    company_id: int = Field(..., gt=0)

class VacancyListUpdate(BaseModel):
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    list_name: Optional[str] = Field(None, min_length=1, max_length=255)

class VacancyListResponse(VacancyListBase):
    id: int
    class Config:
        from_attributes = True