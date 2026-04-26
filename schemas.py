from pydantic import BaseModel, Field
from typing import Optional, Literal, Generic, TypeVar, List
from datetime import date
from decimal import Decimal

EmploymentType = Literal["Полная", "Частичная", "Удаленная", "Проектная"]
Experience = Literal["Без опыта", "1-3 года", "3-5 лет", "5+ лет"]
EnglishLevel = Literal["A1","A2","B1","B2","C1","C2"]
T = TypeVar('T')


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True

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

class VacancyResponse(VacancyBase, BaseResponse):
    id: int
    views_count: int
    applications_count: int
    rating: Optional[float] = Field(None)
    publication_date: Optional[date] = Field(None)
    is_visible: bool


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

class EmployerResponse(EmployerBase, BaseResponse):
    id: int 
    vacancy_count: int 
    rating: Optional[float] = None
    
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

class VacancyListResponse(VacancyListBase, BaseResponse):
    id: int

class ApplicationBase(BaseModel):
    status: Optional[str] = Field(None)

class ApplicationCreate(ApplicationBase):
    vacancy_id: int = Field(..., gt=0)
    resume_id: int = Field(..., gt=0)

class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None)

class ApplicationResponse(ApplicationBase, BaseResponse):
    id: int
    application_date: Optional[date] = Field(None)

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

class SeekerResponse(SeekerBase, BaseResponse):
    id: int 

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

class ResumeResponse(ResumeBase, BaseResponse):
    id: int
    views_count: int
    applications_count: int
    created_at: Optional[date] = Field(None)

class UserRegister(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=5, max_length=255)
    user_type: Literal["employer", "seeker"]
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)

class UserLogin(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=5, max_length=255)
    user_type: Literal["employer", "seeker"]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int
    page_size: int
