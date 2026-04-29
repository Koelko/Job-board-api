from pydantic import BaseModel, Field
from typing import Optional, Literal, Generic, TypeVar, List

T = TypeVar('T')

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