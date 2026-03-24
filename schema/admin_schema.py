from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List, Optional
from datetime import datetime
from schema.blood_test_schema import BloodTestSummary
from schema.spent_naf_schema import SpentNafSummary
from schema.food_log_schema import FoodLogEntry, ExerciseLogEntry


class AdminLoginRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    username: str
    password: str


class AdminLoginResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    token: str
    username: str


class PatientManagementRow(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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
    activity_level: Optional[str]
    latest_spent: Optional[SpentNafSummary]
    latest_blood_test: Optional[BloodTestSummary]
    total_screenings: int


class PatientDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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
    activity_level: Optional[str]
    # Full histories
    spent_naf_history: List[SpentNafSummary]
    blood_test_history: List[BloodTestSummary]
    food_log_history: List[FoodLogEntry]
    exercise_log_history: List[ExerciseLogEntry]
