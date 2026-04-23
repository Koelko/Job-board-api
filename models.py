from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean,Float, Text, Enum, func, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
Base = declarative_base()
class Employer(Base):
    __tablename__ = "companies"
    id = Column("ID", Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column("Phone", String(50), nullable=True)
    vacancy_count = Column(Integer, nullable=True, default=0)
    rating = Column("Rating",Float, nullable=True, default=None)
    email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    vacancy_list = relationship("VacancyList", back_populates="employer")

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column("ID",Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey("vacancy_lists.ID"), nullable=False)
    specialty = Column(String(100), nullable=True)
    salary = Column(Integer, nullable=True)
    publication_date = Column(DateTime, nullable=False, server_default=func.curdate())
    city = Column(String(50), nullable=True, default="Москва")
    employment_type = Column(Enum('Полная', 'Частичная', 'Удаленная', 'Проектная'), nullable=True, default="Полная")
    experience = Column(Enum('Без опыта', '1-3 года', '3-5 лет', '5+ лет'), nullable=True, default="Без опыта")
    key_skills = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=True, default=True)
    views_count = Column(Integer, nullable=True, default=0)
    applications_count = Column(Integer, nullable=True, default=0)
    rating = Column(Float, nullable=True, default=None)
    vacancy_list = relationship("VacancyList", back_populates="vacancy")
    application = relationship("Application", back_populates="vacancy")



class VacancyList(Base):
    __tablename__ = "vacancy_lists"
    id = Column("ID", Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.ID"),nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=False)
    list_name = Column(String(255), nullable=True)
    employer = relationship("Employer", back_populates="vacancy_list")
    vacancy = relationship("Vacancy", back_populates="vacancy_list")


class Application(Base):
    __tablename__ = "applications"
    id = Column("ID",Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey('vacancies.ID'), nullable=False)
    resume_id = Column(Integer, ForeignKey('resumes.ID'), nullable=False)
    status = Column(String(50), nullable=True, default='new')
    application_date = Column(DateTime, nullable=True, server_default=func.curdate())
    vacancy = relationship("Vacancy", back_populates="application")
    resume = relationship("Resume", back_populates="application")

class Seeker(Base):
    __tablename__ = "job_seekers"
    id = Column("ID",Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    resume = relationship("Resume", back_populates="seeker")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column("ID", Integer, primary_key=True)
    seeker_id = Column(Integer, ForeignKey('job_seekers.ID'), nullable=False)
    experience = Column(Text, nullable=True)
    specialty = Column(String(100), nullable=True)
    education = Column(Text, nullable=True)
    city = Column(String(50), nullable=True, default='Москва')
    salary = Column(DECIMAL(10,2), nullable=True)
    employment_type = Column(Enum('Полная','Частичная','Удаленная','Проектная'), nullable=True, default='')
    english_level = Column(Enum('A1','A2','B1','B2','C1','C2'), nullable=True)
    is_active = Column(Enum('Активно','Неактивно'), nullable=True, default='Активно')
    views_count = Column(Integer, nullable=True, default=0)
    applications_count = Column(Integer, nullable=True, default=0)
    rating = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, nullable=True, server_default=func.curdate())
    seeker = relationship("Seeker", back_populates="resume")
    application = relationship("Application", back_populates="resume")

