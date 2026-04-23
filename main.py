from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Vacancy, VacancyList, Employer, Seeker, Resume, Application
from typing import List
import schemas
from auth import router
from dependencies import get_current_employer, get_current_seeker
from math import ceil 

app = FastAPI(title="Биржа труда", description="Учебный проект биржа труда")
app.include_router(router)

@app.get("/")
def read_root():
    return {"message":"Connection successful"}

@app.get("/vacancies", response_model=schemas.PaginatedResponse[schemas.VacancyResponse])
def show_vacancies(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы")):
    total = db.query(Vacancy).count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    vacancies = db.query(Vacancy).offset(offset).limit(page_size).all()
    return {'items': vacancies, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/vacancies", response_model=schemas.VacancyResponse)
def add_vacancy(vacancy: schemas.VacancyCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
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

@app.get("/vacancies/{vacancy_id}", response_model=schemas.VacancyResponse)
def show_current_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy

@app.put("/vacancies/{vacancy_id}", response_model=schemas.VacancyResponse)
def update_vacancy(vacancy_id: int, vacancy: schemas.VacancyUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
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

@app.get("/employers", response_model=schemas.PaginatedResponse[schemas.EmployerResponse])
def show_employers(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=10, le=50, description="Размер страницы" )):
    total = db.query(Employer).count()
    offset = (page - 1)*page_size
    pages = ceil(total / page_size)
    employers = db.query(Employer).offset(offset).limit(page_size).all()
    result = []
    for employer in employers:
        vacancy_count = db.query(Vacancy).join(VacancyList).filter(VacancyList.company_id == employer.id).count()
        result.append({**employer.__dict__, "vacancy_count": vacancy_count})
    return {'items': result, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.get("/employers/{employer_id}", response_model=schemas.EmployerResponse)
def show_current_employer(employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    vacancy_count = db.query(Vacancy).join(VacancyList).filter(VacancyList.company_id == employer_id).count()
    return {**employer.__dict__, "vacancy_count": vacancy_count}

@app.put("/employers/{employer_id}", response_model=schemas.EmployerResponse)
def update_employer(employer_id : int, employer: schemas.EmployerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
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

@app.get("/resumes", response_model=schemas.PaginatedResponse[schemas.ResumeResponse])
def show_resumes(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=10, le=50, description="Размер страницы")):
    total = db.query(Resume).count()
    offset = (page - 1) * page_size
    pages = ceil(total / page_size)
    resumes = db.query(Resume).offset(offset).limit(page_size).all()
    return {'items': resumes, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/resumes", response_model=schemas.ResumeResponse)
def add_resume(resume: schemas.ResumeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_resume = Resume(**resume.model_dump())
    db_resume.seeker_id = current_user['user_id']
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@app.get("/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def show_current_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдена")
    return resume

@app.put("/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def update_resume(resume_id: int, resume: schemas.ResumeUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
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

@app.get("/seekers", response_model=schemas.PaginatedResponse[schemas.SeekerResponse])
def show_seekers(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=10, le=50, description="Размер страницы")):
    total = db.query(Seeker).count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    seekers = db.query(Seeker).offset(offset).limit(page_size).all()
    return {'items': seekers, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.get("/seekers/{seeker_id}", response_model=schemas.SeekerResponse)
def show_current_seeker(seeker_id : int, db: Session = Depends(get_db)):
    seeker = db.query(Seeker).filter(Seeker.id == seeker_id).first()
    if not seeker:
        raise HTTPException(status_code=404, detail="Соискатель не найден")
    return seeker

@app.put("/seekers/{seeker_id}", response_model=schemas.SeekerResponse)
def update_seeker(seeker_id: int, seeker: schemas.SeekerUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
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

@app.get("/applications/my", response_model=schemas.PaginatedResponse[schemas.ApplicationResponse])
def show_applications_seeker(db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=10, le=50, description="Размер страницы")):
    total = db.query(Application).join(Resume).filter(Resume.seeker_id == current_user['user_id']).count()
    pages = ceil (total / page_size)
    offset = (page - 1) * page_size
    applications = db.query(Application).join(Resume).filter(Resume.seeker_id == current_user['user_id']).offset(offset).limit(page_size).all()
    return {'items':applications, 'total':total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.get("/vacancies/{vacancy_id}/applications", response_model=schemas.PaginatedResponse[schemas.ApplicationResponse])
def show_applications_employer(vacancy_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=1, le=50, description="Размер страницы")):
    db_vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    if not db_vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == db_vacancy.list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Такого списка вакансий не существует")
    if current_user['user_id'] != db_vacancy_list.company_id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    total = db.query(Application).filter(Application.vacancy_id == db_vacancy.id).count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    applications = db.query(Application).filter(Application.vacancy_id == db_vacancy.id).offset(offset).limit(page_size).all()
    return {'items': applications, 'total': total, 'page':page, 'pages':pages, 'page_size': page_size}

@app.post("/applications", response_model=schemas.ApplicationResponse)
def add_application(application : schemas.ApplicationCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_seeker)):
    db_application = Application(**application.model_dump())
    cur_res_id = [r.id for r in db.query(Resume).filter(Resume.seeker_id == current_user['user_id']).all()]
    if db_application.resume_id not in cur_res_id:
        raise HTTPException(status_code=403, detail="Нет доступа") 
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.put("/vacancies/{vacancy_id}/applications/{application_id}", response_model=schemas.ApplicationResponse)
def update_application(application_id: int, application: schemas.ApplicationUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
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

@app.get("/vacancy-lists", response_model=schemas.PaginatedResponse[schemas.VacancyListResponse])
def show_vacancy_list(db: Session = Depends(get_db), page: int = Query(1, ge=1, description="Номер страницы"), page_size: int = Query(10, ge=10, le=50, description="Размер страницы")):
    total = db.query(VacancyList).count()
    pages = ceil(total / page_size)
    offset = (page - 1) * page_size
    vacancy_list = db.query(VacancyList).offset(offset).limit(page_size).all()
    return {'items': vacancy_list, 'total': total, 'page': page, 'pages': pages, 'page_size': page_size}

@app.post("/vacancy-lists", response_model=schemas.VacancyListResponse)
def add_vacancy_list(vacancy_list: schemas.VacancyListCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
    db_vacancy_list = VacancyList(**vacancy_list.model_dump())
    db_vacancy_list.company_id = current_user['user_id']
    db.add(db_vacancy_list)
    db.commit()
    db.refresh(db_vacancy_list)
    return db_vacancy_list

@app.get("/vacancy-lists/{vacancy_list_id}", response_model=schemas.VacancyListResponse)
def show_current_vacancy_list(vacancy_list_id: int, db: Session = Depends(get_db)):
    db_vacancy_list = db.query(VacancyList).filter(VacancyList.id == vacancy_list_id).first()
    if not db_vacancy_list:
        raise HTTPException(status_code=404, detail="Список вакансий не обнаружен")
    return db_vacancy_list

@app.put("/vacancy-lists/{vacancy_list_id}", response_model=schemas.VacancyListResponse)
def update_vacancy_list(vacancy_list_id: int, vacancy_list: schemas.VacancyListUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_employer)):
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