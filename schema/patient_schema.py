from typing import List, Optional
from schema.base_schema import BaseSchema


class PatientProfileBase(BaseSchema):
    first_name: str
    last_name: str
    age: int
    gender: str
    phone: str

    height: float
    weight: float
    blood_pressure: str

    existing_diseases: List[str]

    smoking: str
    alcohol: str
    activity_level: str


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None

    height: Optional[float] = None
    weight: Optional[float] = None
    blood_pressure: Optional[str] = None

    existing_diseases: Optional[List[str]] = None

    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    activity_level: Optional[str] = None


class PatientProfileRead(BaseSchema):
    id: int
    user_id: int

    first_name: str
    last_name: str
    age: int
    gender: str
    phone: str

    height: float
    weight: float
    bmi: Optional[float]
    blood_pressure: str

    existing_diseases: List[str]

    smoking: str
    alcohol: str
    activity_level: str
