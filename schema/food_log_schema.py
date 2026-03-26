from typing import Optional
from schema.base_schema import BaseSchema
from datetime import datetime


class FoodLogCreate(BaseSchema):
    food_name: str
    calories: float
    protein: float = 0
    sodium: float = 0
    potassium: float = 0
    phosphorus: float = 0
    meal_category: str = "Snack"
    eaten_date: str  # "YYYY-MM-DD"


class FoodLogRead(BaseSchema):
    id: int
    user_id: int
    food_name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    meal_category: str
    eaten_date: str
    created_at: Optional[datetime]


class ExerciseLogCreate(BaseSchema):
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str  # "YYYY-MM-DD"


class ExerciseLogRead(BaseSchema):
    id: int
    user_id: int
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str
    created_at: Optional[datetime]


class DailyCalorieGoalRead(BaseSchema):
    user_id: int
    daily_goal: int


class DailyCalorieGoalUpdate(BaseSchema):
    daily_goal: int


class FoodLogUpdate(BaseSchema):
    food_name: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    meal_category: Optional[str] = None


class FoodLogEntry(BaseSchema):
    id: int
    food_name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    meal_category: str
    eaten_date: str
    created_at: Optional[datetime]


class ExerciseLogEntry(BaseSchema):
    id: int
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str
    created_at: Optional[datetime]
