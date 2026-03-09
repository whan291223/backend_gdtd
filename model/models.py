from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone
from enum import Enum

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    line_user_id: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    picture_url: Optional[str] = None

    real_name: Optional[str] = None
    surname: Optional[str] = None

