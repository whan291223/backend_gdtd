from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schema.config import common_config


class FoodLogCreate(BaseModel):
    model_config = common_config

    food_name: str
    calories: float
    protein: float = 0
    sodium: float = 0
    potassium: float = 0
    phosphorus: float = 0
    volume: Optional[float] = None
    meal_category: str = "Snack"
    eaten_date: str  # "YYYY-MM-DD"


class FoodLogRead(BaseModel):
    model_config = common_config

    id: int
    user_id: int
    food_name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    volume: Optional[float] = None
    meal_category: str
    eaten_date: str
    created_at: Optional[datetime]


class ExerciseLogCreate(BaseModel):
    model_config = common_config

    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str  # "YYYY-MM-DD"


class ExerciseLogRead(BaseModel):
    model_config = common_config

    id: int
    user_id: int
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str
    created_at: Optional[datetime]


class FoodLogUpdate(BaseModel):
    model_config = common_config

    food_name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    volume: Optional[float] = None
    meal_category: Optional[str] = None


class FoodLogEntry(BaseModel):
    model_config = common_config

    id: int
    food_name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    volume: Optional[float] = None
    meal_category: str
    eaten_date: str
    created_at: Optional[datetime]


class ExerciseLogEntry(BaseModel):
    model_config = common_config

    id: int
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str
    created_at: Optional[datetime]

class DailySetupCreate(BaseModel):
    model_config = common_config
    weight: float
    urine_amount: Optional[float] = None
    setup_date: str  # YYYY-MM-DD


# --- Food Database -----------------------------------------------------------

class FoodDatabaseCreate(BaseModel):
    model_config = common_config
    name: str
    calories: float
    protein: float = 0
    sodium: float = 0
    potassium: float = 0
    phosphorus: float = 0
    volume: Optional[float] = None


class FoodDatabaseUpdate(BaseModel):
    model_config = common_config
    name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    volume: Optional[float] = None


class FoodDatabaseRead(BaseModel):
    model_config = common_config
    id: int
    name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    volume: Optional[float] = None


# --- Exercise Database -------------------------------------------------------

class ExerciseDatabaseCreate(BaseModel):
    model_config = common_config
    name: str
    met: float


class ExerciseDatabaseUpdate(BaseModel):
    model_config = common_config
    name: Optional[str] = None
    met: Optional[float] = None


class ExerciseDatabaseRead(BaseModel):
    model_config = common_config
    id: int
    name: str
    met: float

class DailySetupUpdate(BaseModel):
    model_config = common_config
    weight: Optional[float] = None
    urine_amount: Optional[float] = None

class DailySetupRead(BaseModel):
    model_config = common_config
    weight: float
    urine_amount: Optional[float] = None
    setup_date: str  # YYYY-MM-DD
