import bcrypt, jwt, os
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime, timedelta, timezone

load_dotenv()
secret_key = os.getenv("SECRET_KEY")

def hash_password(password: str) -> str:
    password_byte = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_byte, salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    password_byte = password.encode('utf-8')
    hashed_byte = hashed.encode('utf-8')
    return bcrypt.checkpw(password_byte, hashed_byte)

def create_access_token(payload: dict) -> str:
    token_playload = {**payload, 'exp': datetime.now(timezone.utc) + timedelta(hours=3)}
    return jwt.encode(token_playload, secret_key, algorithm='HS256')

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError as e:
        print (f"Token is bad: {e}")
        return None
    except jwt.InvalidTokenError as e:
        print (f"Token is bad: {e}")
        return None
