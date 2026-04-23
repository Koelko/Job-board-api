from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from security import verify_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return payload

def get_current_employer(user: dict = Depends(get_current_user)):
    if user['user_type'] != "employer":
        raise HTTPException(status_code=403, detail="Только для работодателей")
    return user

def get_current_seeker(user: dict = Depends(get_current_user)):
    if user['user_type'] != "seeker":
        raise HTTPException(status_code=403, detail="Только для соискателей")
    return user