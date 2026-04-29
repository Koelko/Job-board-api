from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db
from backend.models import Vacancy, VacancyList, Employer, Seeker, Resume, Application
from sqlalchemy import or_, desc, asc
from auth import router
from dependencies import get_current_employer, get_current_seeker
from math import ceil 
from typing import List, Optional
from backend.schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate, UserLogin, UserRegister, Token, PaginatedResponse, ResumeCreate, ResumeResponse, ResumeUpdate, EmployerCreate, EmployerResponse, EmployerUpdate, SeekerCreate, SeekerResponse, SeekerUpdate, VacancyListUpdate, VacancyCreate, VacancyListCreate, VacancyListResponse, VacancyResponse, VacancyUpdate
from constants import ALLOWED_EMPLOYMENT_TYPES, ALLOWED_EXPERIENCE, ALLOWED_STATUS, ALLOWED_APPLICATION_SORT, ALLOWED_EMPLOYER_SORT, ALLOWED_RESUME_SORT, ALLOWED_VACANCY_SORT

app = FastAPI(title="Биржа труда", description="Учебный проект биржа труда")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/")
def read_root():
    return {"message":"Connection successful"}

@app.get("/vacancies", response_model=PaginatedResponse[VacancyResponse])
def show_vacancies(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы"),
                   city: Optional[str] = Query(None, description="Город"), salary_min: Optional[float] = Query(None, ge=0, description="Минимальная зарплата"), 
                   experience: Optional[str] = Query(None, description="Опыт работы"), employment_type: Optional[str] = Query(None, description="Тип занятости"), 
                   search: Optional[str] = Query(None, description="Должность, компания, навык"), sort: str = Query("publication_date"),
                    order: str = Query("desc")):
    query = db.query(Vacancy)
    if sort not in ALLOWED_VACANCY_SORT:
        raise HTTPException(status_code=400, detail=f"Недопустимое поле. Разрешено: {ALLOWED_VACANCY_SORT}")
    if order not in ['desc', 'asc']:
        raise HTTPException(status_code=400, detail="order должен быть 'asc' или 'desc'")
    sort_column = getattr(Vacancy, sort)
    query = query.order_by(desc(sort_column) if order == "desc" else asc(sort_column))
    if city:
        query = query.filter(Vacancy.city == city)
    if salary_min:
        query = query.filter(Vacancy.salary >= salary_min)
    if experience and experience in ALLOWED_EXPERIENCE:
        query = query.filter(Vacancy.experience == experience)
    if employment_type and employment_type in ALLOWED_EMPLOYMENT_TYPES:
        query = query.filter(Vacancy.employment_type == employment_type)
    if search:
        conditions = [Vacancy.specialty.ilike(f"%{search}%")]
        conditions.extend([Vacancy.key_skills.ilike("%{skill.strip()}%") for skill in search.split(",")])
        employer_ids = [e[0] for e in db.query(VacancyList.company_id).join(Employer).filter(Employer.name.ilike(f"%{search}%")).all()]
        if employer_ids:
            vacancy_list_ids = [vl[0] for vl in db.query(VacancyList.id).filter(VacancyList.company_id.in_(employer_ids)).all()]
            if vacancy_list_ids:
                conditions.append(Vacancy.list_id.in_(vacancy_list_ids))
        query = query.filter(or_*conditions)
    total = query.count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    vacancies = query.offset(offset).limit(page_size).all()
    result = []
    for vacancy in vacancies:
        vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy.list_id).first()
        employer_name = None
        if vacancy_list and vacancy_list.company_id:
            employer = db.query(Employer).filter(Employer.id == vacancy_list.company_id).first()
            if employer:
                employer_name = employer.name
        vacancy_d = {'id': vacancy.id, 'specialty': vacancy.specialty,'salary': vacancy.salary,'city': vacancy.city,
            'experience': vacancy.experience,'employment_type': vacancy.employment_type,'key_skills': vacancy.key_skills,
            'employer_name': employer_name, 'views_count': vacancy.views_count if hasattr(vacancy, 'views_count') else 0,
            'applications_count': vacancy.applications_count if hasattr(vacancy, 'applications_count') else 0,
            'is_visible': vacancy.is_visible if hasattr(vacancy, 'is_visible') else True}
        result.append(vacancy_d)
    return {'items': result, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/vacancies", response_model=VacancyResponse)
def add_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Такого списка вакансий не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db_vacancy = Vacancy(**vacancy.model_dump())
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy          

@app.get("/vacancies/{vacancy_id}", response_model=VacancyResponse)
def show_current_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy

@app.put("/vacancies/{vacancy_id}", response_model=VacancyResponse)
def update_vacancy(vacancy_id: int, vacancy: VacancyUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == db_vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Такого списка вакансий не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    update_vacancy = vacancy.model_dump(exclude_unset=True)
    for field, value in update_vacancy.items():
        setattr(db_vacancy, field, value)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

@app.delete("/vacancies/{vacancy_id}")
def delete_vacancy(vacancy_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == db_vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Такого списка вакансий не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db.delete(db_vacancy)
    db.commit()
    return {"message": "Вакансия удалена"}

@app.get("/employers", response_model=PaginatedResponse[EmployerResponse])
def show_employers(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы" ),
                   search: Optional[str] = Query(None, description="Наименование компании"), sort: Optional[str] = Query(None, description="Поле для сортировки"),
                   order: Optional[str] = Query(None, description="Направление")):
    query = db.query(Employer)
    if sort:
        if sort not in ALLOWED_EMPLOYER_SORT:
            raise HTTPException(status_code=400, detail=f"Недопустимое поле. Разрешено: {ALLOWED_EMPLOYER_SORT}")
        if order not in ['asc', 'desc']:
            raise HTTPException(400, "order должен быть 'asc' или 'desc'")
        sort_column = getattr(Employer, sort)
        query = query.order_by(desc(sort_column) if order == "desc" else asc(sort_column))
    if search:
        query = query.filter(Employer.name.ilike(f"%{search}%"))
    total = query.count()
    offset = (page - 1)*page_size
    pages = ceil(total / page_size)
    employers = query.offset(offset).limit(page_size).all()
    result = []
    for employer in employers:
        vacancy_count = db.query(Vacancy).join(VacancyList).filter(VacancyList.company_id == employer.id).count()
        result.append({**employer.__dict__, "vacancy_count": vacancy_count})
    return {'items': result, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.get("/employers/{employer_id}", response_model=EmployerResponse)
def show_current_employer(employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    vacancy_count = db.query(Vacancy).join(VacancyList).filter(VacancyList.company_id == employer_id).count()
    return {**employer.__dict__, "vacancy_count": vacancy_count}

@app.get("/employer/my", response_model=EmployerResponse)
def get_my_employer_profile(db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    employer = db.query(Employer).filter(Employer.id == current_user['user_id']).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return employer

@app.put("/employers/{employer_id}", response_model=EmployerResponse)
def update_employer(employer_id : int, employer: EmployerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not db_employer:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    if current_user['user_id'] != db_employer.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    update_employer = employer.model_dump(exclude_unset=True)
    for field, value in update_employer.items():
        setattr(db_employer, field, value)
    db.commit()
    db.refresh(db_employer)
    return db_employer

@app.delete("/employers/{employer_id}")
def delete_employer(employer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not db_employer:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    if current_user['user_id'] != db_employer.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db.delete(db_employer)
    db.commit()
    return {"message": "Компания удалена"}

@app.get("/resumes", response_model=PaginatedResponse[ResumeResponse])
def show_resumes(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы"),
                 city: Optional[str] = Query(None, description="Город"), speciality: Optional[str] = Query(None, description="Специальность"),
                 sort: Optional[str] = Query(None, description="Поле для сортировки"), order: Optional[str] = Query(None, description="Направление")):
    query = db.query(Resume)
    if sort:
        if sort not in ALLOWED_RESUME_SORT:
            raise HTTPException(status_code=400, detail=f"Недопустимое поле. Разрешено: {ALLOWED_RESUME_SORT}")
        if order not in ['desc', 'asc']:
            raise HTTPException(status_code=400, detail="сортировка возможна только по возрастанию или убыванию")
        sort_column = getattr(Resume, sort)
        query = query.order_by(desc(sort_column) if order == 'desc' else asc(sort_column))
    if city:
        query = query.filter(Resume.city == city)
    if speciality:
        query = query.filter(Resume.specialty == speciality)
    total = query.count()
    offset = (page - 1) * page_size
    pages = ceil(total / page_size)
    resumes = query.offset(offset).limit(page_size).all()
    return {'items': resumes, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/resumes", response_model=ResumeResponse)
def add_resume(resume: ResumeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_resume = Resume(**resume.model_dump())
    db_resume.seeker_id = current_user['user_id']
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@app.get("/resumes/{resume_id}", response_model=ResumeResponse)
def show_current_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдена")
    return resume

@app.put("/resumes/{resume_id}", response_model=ResumeResponse)
def update_resume(resume_id: int, resume: ResumeUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
       raise  HTTPException(status_code=404, detail="Резюме не найдено")
    if current_user['user_id'] != db_resume.seeker_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    update_resume = resume.model_dump(exclude_unset=True)
    for field, value in update_resume.items():
        setattr(db_resume, field, value)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@app.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    if current_user['user_id'] != db_resume.seeker_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db.delete(db_resume)
    db.commit()
    return {"message":"Резюме удалено"}

@app.get("/seeker/my", response_model=SeekerResponse)
def show_my_seeker_profile(db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    seeker = db.query(Seeker).filter(Seeker.id == current_user['user_id']).first()
    if not seeker:
        raise HTTPException(status_code=404, detail="Соискатель не найден")
    return seeker

@app.put("/seekers/{seeker_id}", response_model=SeekerResponse)
def update_seeker(seeker_id: int, seeker: SeekerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_seeker = db.query(Seeker).filter(Seeker.id == seeker_id).first()
    if not db_seeker:
        raise HTTPException(status_code=404, detail="Соискатель не найден")
    if current_user['user_id'] != db_seeker.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    update_seeker = seeker.model_dump(exclude_unset=True)
    for field, value in update_seeker.items():
        setattr(db_seeker, field, value)
    db.commit()
    db.refresh(db_seeker)
    return db_seeker

@app.delete("/seekers/{seeker_id}")
def delete_seeker(seeker_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_seeker = db.query(Seeker).filter(Seeker.id == seeker_id).first()
    if not db_seeker:
        raise HTTPException(status_code=404, detail="Соискатель не найден")
    if current_user['user_id'] != db_seeker.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db.delete(db_seeker)
    db.commit()
    return {"message":"Соискатель удален"}

@app.get("/applications/my", response_model=PaginatedResponse[ApplicationResponse])
def show_applications_seeker(db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы")):
    total = db.query(Application).join(Resume).filter(Resume.seeker_id == current_user['user_id']).count()
    pages = ceil (total / page_size)
    offset = (page - 1) * page_size
    applications = db.query(Application).join(Resume).filter(Resume.seeker_id == current_user['user_id']).offset(offset).limit(page_size).all()
    return {'items':applications, 'total':total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.get("/vacancies/{vacancy_id}/applications", response_model=PaginatedResponse[ApplicationResponse])
def show_applications_employer(vacancy_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы"),
                               status: Optional[str] = Query(None, description="Статус отклика"), sort: Optional[str] = Query(None, description="Поле сортировки"),
                               order: Optional[str] = Query(None, description="Направление")):
    db_vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == db_vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Такого списка вакансий не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    query = db.query(Application).filter(Application.vacancy_id == db_vacancy.id)
    if sort:
        if sort not in ALLOWED_APPLICATION_SORT:
            raise HTTPException(status_code=400, detail=f"Недопустимое значение. Разрешено: {ALLOWED_APPLICATION_SORT}")
        if order not in ['desc', 'asc']:
            raise HTTPException(status_code=400, detail="только desc или asc")
        sort_column = getattr(Application, sort)
        query = query.order_by(desc(sort_column) if order == 'desc' else asc(sort_column))
    if status:
        if status not in ALLOWED_STATUS:
            raise HTTPException(status_code=400, detail=f"Недопустимое значение. Разрешено: {ALLOWED_STATUS}")
        query = query.filter(Application.status == status)
    total = query.count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    applications = query.offset(offset).limit(page_size).all()
    return {'items': applications, 'total': total, 'page':page, 'pages':pages, 'page_size': page_size}

@app.post("/applications", response_model=ApplicationResponse)
def add_application(application : ApplicationCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_application = Application(**application.model_dump())
    cur_res_id = [r.id for r in db.query(Resume).filter(Resume.seeker_id == current_user['user_id']).all()]
    if db_application.resume_id not in cur_res_id:
        raise HTTPException(status_code=403, detail="Нет доступа") 
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.put("/vacancies/{vacancy_id}/applications/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, application: ApplicationUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    db_vacancy = db.query(Vacancy).filter(Vacancy.id == db_application.vacancy_id).first()
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Вакансии не существует")
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == db_vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Вакансии не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    update_application = application.model_dump(exclude_unset=True)
    for field, value in update_application.items():
        setattr(db_application, field, value)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.delete("/applications/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="отклик не найден")
    resumes = [r.id for r in db.query(Resume).filter(Resume.seeker_id == current_user['user_id']).all()]
    if db_application.resume_id not in resumes:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    db.delete(db_application)
    db.commit()
    return {"message":"Отклик удален"}

@app.get("/vacancy-lists", response_model=PaginatedResponse[VacancyListResponse])
def show_vacancy_list(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы")):
    total = db.query(VacancyList).count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    vacancy_list = db.query(VacancyList).offset(offset).limit(page_size).all()
    return {'items': vacancy_list, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/vacancy-lists", response_model=VacancyListResponse)
def add_vacancy_list(vacancy_list: VacancyListCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy_list = VacancyList(**vacancy_list.model_dump())
    db_vacancy_list.company_id = current_user['user_id']
    db.add(db_vacancy_list)
    db.commit()
    db.refresh(db_vacancy_list)
    return db_vacancy_list

@app.get("/vacancy-lists/{vacancy_list_id}", response_model=VacancyListResponse)
def show_current_vacancy_list(vacancy_list_id: int, db: Session = Depends(get_db)):
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy_list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Список вакансий не обнаружен")
    return db_vacancy_list

@app.put("/vacancy-lists/{vacancy_list_id}", response_model=VacancyListResponse)
def update_vacancy_list(vacancy_list_id: int, vacancy_list: VacancyListUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy_list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Список вакансий не обнаружен")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Прав доступа нет")
    update_vacancy_list = vacancy_list.model_dump(exclude_unset=True)
    for field, value in update_vacancy_list.items():
        setattr(db_vacancy_list, field, value)
    db.commit()
    db.refresh(db_vacancy_list)
    return db_vacancy_list

@app.delete("/vacancy-lists/{vacancy_list_id}")
def delete_vacancy_list(vacancy_list_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy_list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Список вакансий не обнаружен")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Прав доступа нет")
    db.delete(db_vacancy_list)
    db.commit()
    return {"message":"Список вакансий удален"}