from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

EmploymentType = Literal["Полная", "Частичная", "Удаленная", "Проектная"]
Experience = Literal["Без опыта", "1-3 года", "3-5 лет", "5+ лет"]
EnglishLevel = Literal["A1","A2","B1","B2","C1","C2"]

class VacancyBase(BaseModel):
    specialty: str  = Field(..., min_length=1, max_length=100)
    salary: Optional[int] = Field(None, ge=0)
    city: Optional[str] = Field('Москва',min_length=1, max_length=50)
    employment_type: Optional[EmploymentType] = Field("Полная")
    experience: Optional[Experience] = Field("Без опыта")
    key_skills: Optional[str] = Field(None)

class VacancyCreate(VacancyBase):
    list_id: int = Field(..., gt=0)

class VacancyUpdate(BaseModel):
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[int] = Field(None, ge=0)
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    employment_type: Optional[EmploymentType] = Field(None)
    experience: Optional[Experience] = Field(None)
    key_skills: Optional[str] = Field(None)
    is_visible: Optional[bool] = Field(None)

class VacancyResponse(VacancyBase):
    id: int
    views_count: int
    applications_count: int
    employer_name: Optional[str] = None
    rating: Optional[float] = Field(None)
    publication_date: Optional[date] = Field(None)
    is_visible: bool
    class Config:
        from_attributes = True