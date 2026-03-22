from pydantic import BaseModel
from typing import List, Optional


class PatientProfileBase(BaseModel):
    firstName: str
    lastName: str
    age: int
    gender: str
    phone: str

    height: float
    weight: float
    bloodPressure: str

    existingDiseases: List[str]

    smoking: str
    alcohol: str
    activityLevel: str


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None

    height: Optional[float] = None
    weight: Optional[float] = None
    bloodPressure: Optional[str] = None

    existingDiseases: Optional[List[str]] = None

    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    activityLevel: Optional[str] = None


class PatientProfileRead(BaseModel):
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