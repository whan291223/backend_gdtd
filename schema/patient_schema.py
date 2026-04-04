from pydantic import BaseModel
from typing import List, Optional
from schema.config import common_config
from schema.nutrition_schema import NutritionTargets


class PatientProfileBase(BaseModel):
    model_config = common_config

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
    urine_amount: Optional[float] = None


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseModel):
    model_config = common_config

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
    urine_amount: Optional[float] = None


class PatientProfileRead(BaseModel):
    model_config = common_config

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
    urine_amount: Optional[float] = None

    nutrition_targets: Optional[NutritionTargets] = None
