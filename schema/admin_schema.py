from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schema.blood_test_schema import BloodTestSummary
from schema.spent_naf_schema import SpentNafSummary
from schema.food_log_schema import FoodLogEntry, ExerciseLogEntry
from schema.config import common_config


class AdminLoginRequest(BaseModel):
    model_config = common_config

    username: str
    password: str


class AdminLoginResponse(BaseModel):
    model_config = common_config

    token: str
    username: str


class PatientManagementRow(BaseModel):
    model_config = common_config

    user_id: int
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    blood_pressure: Optional[str] = None
    existing_diseases: Optional[List[str]] = None
    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    urine_amount: Optional[float] = None
    latest_spent: Optional[SpentNafSummary] = None
    latest_blood_test: Optional[BloodTestSummary] = None
    total_screenings: int


class PatientDetail(BaseModel):
    model_config = common_config

    # Identity
    user_id: int
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    # Profile
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    blood_pressure: Optional[str] = None
    existing_diseases: Optional[List[str]] = None
    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    urine_amount: Optional[float] = None
    # Full histories
    spent_naf_history: List[SpentNafSummary]
    blood_test_history: List[BloodTestSummary]
    food_log_history: List[FoodLogEntry]
    exercise_log_history: List[ExerciseLogEntry]
