from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schema.blood_test_schema import BloodTestSummary
from schema.spent_naf_schema import SpentNafSummary
from schema.food_log_schema import FoodLogEntry, ExerciseLogEntry, DailySetupRead
from schema.lab_schema import LabRecordRead, LabCategoryRead
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
    display_name: Optional[str]
    picture_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    phone: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    blood_pressure: Optional[str]
    existing_diseases: Optional[List[str]]
    smoking: Optional[str]
    alcohol: Optional[str]
    urine_amount: Optional[float]
    latest_spent: Optional[SpentNafSummary]
    latest_blood_test: Optional[BloodTestSummary]
    total_screenings: int


class PatientDetail(BaseModel):
    model_config = common_config

    # Identity
    user_id: int
    line_user_id: str
    display_name: Optional[str]
    picture_url: Optional[str]
    # Profile
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    phone: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    blood_pressure: Optional[str]
    existing_diseases: Optional[List[str]]
    smoking: Optional[str]
    alcohol: Optional[str]
    urine_amount: Optional[float]
    # Profile today
    daily_setup: Optional[DailySetupRead] = None
    # Full histories
    spent_naf_history: List[SpentNafSummary]
    blood_test_history: List[BloodTestSummary]
    food_log_history: List[FoodLogEntry]
    exercise_log_history: List[ExerciseLogEntry]
    lab_history: List[LabRecordRead] = []
    lab_config: List[LabCategoryRead] = []
