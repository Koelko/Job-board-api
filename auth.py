import schemas
from database import get_db
from models import Employer, Seeker
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from security import check_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Авторизация"])
@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if user.user_type == "employer":
        db_employer = db.query(Employer).filter(Employer.email == user.email).first()
        if db_employer:
            raise HTTPException(status_code=409, detail="Работодатель с такой почтой уже существует, войдите")
        password_hash = hash_password(user.password)
        employer = Employer(name=user.name, phone=user.phone, email=user.email, password=password_hash, password_hash=user.password)
        db.add(employer)
        db.commit()
        db.refresh(employer)
        token = create_access_token({"user_id": employer.id, "user_type": "employer"})

    elif user.user_type == "seeker":
        db_seeker = db.query(Seeker).filter(Seeker.email == user.email).first()
        if db_seeker:
            raise HTTPException(status_code=409, detail="Соискатель с такой почтой уже существует, войдите")
        password_hash = hash_password(user.password)
        seeker = Seeker(full_name=user.name, phone=user.phone, email=user.email, password=user.password, password_hash=password_hash)
        db.add(seeker)
        db.commit()
        db.refresh(seeker)
        token = create_access_token({"user_id": seeker.id, "user_type": "seeker"})    

    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    if user.user_type == "employer":
        employer = db.query(Employer).filter(Employer.email == user.email).first()
        if not employer:
            raise HTTPException(status_code=404, detail="Работодатель не найден, зарегистрируйтесь")
        db_password_hash = employer.password
        if not check_password(user.password, db_password_hash):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        token = create_access_token({"user_id": employer.id, "user_type": "employer"}) 

    elif user.user_type == "seeker":
        seeker = db.query(Seeker).filter(Seeker.email == user.email).first()
        if not seeker:
            raise HTTPException(status_code=404, detail="Соискатель не найден, зарегистрируйтесь")
        db_password_hash = seeker.password_hash
        if not check_password(user.password, db_password_hash):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        token = create_access_token({"user_id": seeker.id, "user_type": "seeker"})   
    
    return {"access_token": token, "token_type": "bearer"}
    
    