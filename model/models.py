from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ARRAY, Integer, String, JSON

from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    line_user_id: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    picture_url: Optional[str] = None

    real_name: Optional[str] = None
    surname: Optional[str] = None


class SpentNafScore(SQLModel, table=True):
    __tablename__ = "user_answer_table"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None)

    # SPENT: store raw 0/1 per question — scoring done server-side
    user_answer_spent: List[int] = Field(
        default=[],
        sa_column=Column(ARRAY(Integer), nullable=True)
    )
    spent_score: Optional[int] = Field(default=None)

    is_high_risk: Optional[bool] = Field(default=None)

    # NAF: store structured form answers as JSON — scoring done server-side
    user_answer_naf: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    naf_score: Optional[int] = Field(default=None)

    status: str = Field(default="pending_spent")

    submitted_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class BloodTest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")

    serum_albumin:  Optional[float] = Field(default=None)   # g/dL
    npcr:           Optional[float] = Field(default=None)   # g/kg/day
    bun:            Optional[float] = Field(default=None)   # mg/dL
    creatinine:     Optional[float] = Field(default=None)   # mg/dL
    cholesterol:    Optional[float] = Field(default=None)   # mg/dL
    hemoglobin:     Optional[float] = Field(default=None)   # g/dL
    hematocrit:     Optional[float] = Field(default=None)   # %
    potassium:      Optional[float] = Field(default=None)   # mEq/L
    phosphorus:     Optional[float] = Field(default=None)   # mg/dL
    bicarbonate:    Optional[float] = Field(default=None)   # mEq/L

    note: Optional[str] = Field(default=None)
    recorded_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class FoodLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    food_name: str
    calories: int
    meal_category: str = Field(default="Snack")
    eaten_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class DailyCalorieGoal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, unique=True)
    daily_goal: int = Field(default=2000)


class PatientProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(index=True, foreign_key="user.id")

    first_name: str
    last_name: str
    age: int
    gender: str
    phone: str

    height: float
    weight: float
    bmi: Optional[float] = None
    blood_pressure: str

    # ✅ Use PG_ARRAY(Text) — avoids the VARCHAR[] cast compile error
    existing_diseases: List[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String), nullable=True)
    )

    smoking: str
    alcohol: str
    activity_level: str

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )