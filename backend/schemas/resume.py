from pydantic import BaseModel, Field
from typing import Optional, Literal, TypeVar
from datetime import date
from decimal import Decimal

EmploymentType = Literal["Полная", "Частичная", "Удаленная", "Проектная"]
Experience = Literal["Без опыта", "1-3 года", "3-5 лет", "5+ лет"]
EnglishLevel = Literal["A1","A2","B1","B2","C1","C2"]
T = TypeVar('T')


class ResumeBase(BaseModel):
    experience: Optional[Experience] = Field(None)
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    education: Optional[str] = Field(None)
    city: Optional[str] = Field('Москва', min_length=1, max_length=50)
    salary: Optional[Decimal] = Field(None, ge=0)
    employment_type: Optional[EmploymentType] = Field('Полная')
    english_level: Optional[EnglishLevel] = Field(None)
    is_active: Optional[Literal["Активно", "Неактивно"]] = Field('Активно')

class ResumeCreate(ResumeBase):
    seeker_id: int = Field(..., gt=0)

class ResumeUpdate(BaseModel):
    experience: Optional[Experience] = Field(None)
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    education: Optional[str] = Field(None)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[Decimal] = Field(None, ge=0)
    employment_type: Optional[EmploymentType] = Field(None)
    english_level: Optional[EnglishLevel] = Field(None )
    is_active: Optional[Literal["Активно", "Неактивно"]] = Field(None)

class ResumeResponse(ResumeBase):
    id: int
    views_count: int
    applications_count: int
    created_at: Optional[date] = Field(None)
    class Config:
        from_attributes = True