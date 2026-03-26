from typing import Optional
from schema.base_schema import BaseSQLSchema


class UserCreate(BaseSQLSchema):
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    real_name: Optional[str] = None
    surname: Optional[str] = None

class UserUpdate(BaseSQLSchema):
    real_name: str
    surname: Optional[str] = None


class UserRead(BaseSQLSchema):
    id: int
    line_user_id: str
    display_name: Optional[str]
    picture_url: Optional[str]
    real_name: Optional[str]