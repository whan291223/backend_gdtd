from sqlmodel import SQLModel
from typing import Optional
from schema.config import common_config


class UserCreate(SQLModel):
    model_config = common_config

    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    real_name: Optional[str] = None
    surname: Optional[str] = None

class UserUpdate(SQLModel):
    model_config = common_config

    real_name: str
    surname: Optional[str] = None


class UserRead(SQLModel):
    model_config = common_config

    id: int
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    real_name: Optional[str] = None