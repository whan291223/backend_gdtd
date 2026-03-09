from sqlmodel import SQLModel
from typing import Optional


class UserCreate(SQLModel):
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    real_name: Optional[str] = None
    surname: Optional[str] = None

class UserUpdate(SQLModel):
    real_name: str
    surname: Optional[str] = None


class UserRead(SQLModel):
    id: int
    line_user_id: str
    display_name: Optional[str]
    picture_url: Optional[str]
    real_name: Optional[str]