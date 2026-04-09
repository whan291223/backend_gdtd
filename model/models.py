from typing import List, Optional, Dict, Any
import uuid
from uuid import UUID as UUID_TYPE
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import ARRAY, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    line_user_id: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    picture_url: Optional[str] = None

    real_name: Optional[str] = None
    surname: Optional[str] = None

    # daily_setups: List["DailySetup"] = Relationship(back_populates="user")
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
    naf_score_breakdown: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
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
    user_id: int = Field(index=True, foreign_key="user.id")
    food_name: str
    calories: float = Field(default=0)
    protein: float = Field(default=0)       # g
    sodium: float = Field(default=0)        # mg
    potassium: float = Field(default=0)     # mg
    phosphorus: float = Field(default=0)    # mg
    meal_category: str = Field(default="Snack")  # Breakfast | Lunch | Dinner | Snack
    eaten_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    volume: Optional[float] = Field(default=None)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class DailySetup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    weight: float    
    urine_amount: Optional[float] = Field(default=None)
    setup_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    # Use Relationship from sqlmodel for better compatibility
    # user: "User" = Relationship(back_populates="daily_setups")

class ExerciseLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


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
        sa_column=Column(PG_ARRAY(Text), nullable=True)
    )

    smoking: str
    alcohol: str
    urine_amount: Optional[float]= Field(default=None)
    nutrition_targets: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class FoodDatabase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    calories: float = Field(default=0)
    protein: float = Field(default=0)    # g
    sodium: float = Field(default=0)     # mg
    potassium: float = Field(default=0)  # mg
    phosphorus: float = Field(default=0) # mg


class LabCategory(SQLModel, table=True):
    __tablename__ = "lab_categories"

    id: UUID_TYPE = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    display_order: Optional[int] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    fields: List["LabField"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "LabField.display_order"}
    )


class LabField(SQLModel, table=True):
    __tablename__ = "lab_fields"

    id: UUID_TYPE = Field(default_factory=uuid.uuid4, primary_key=True)
    category_id: UUID_TYPE = Field(foreign_key="lab_categories.id")
    name: str
    unit: str
    display_order: Optional[int] = None

    category: LabCategory = Relationship(back_populates="fields")
    # Add cascade delete
    values: List["LabValue"] = Relationship(
        back_populates="field",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class LabRecord(SQLModel, table=True):
    __tablename__ = "lab_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    note: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    values: List["LabValue"] = Relationship(
        back_populates="record",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class LabValue(SQLModel, table=True):
    __tablename__ = "lab_values"

    id: Optional[int] = Field(default=None, primary_key=True)
    record_id: int = Field(foreign_key="lab_records.id")
    field_id: UUID_TYPE = Field(foreign_key="lab_fields.id")
    value: Optional[float] = Field(default=None)

    record: LabRecord = Relationship(back_populates="values")
    field: LabField = Relationship(back_populates="values")