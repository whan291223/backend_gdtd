from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


MEAL_CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack"]


class FoodLogCreate(BaseModel):
    user_id: int
    food_name: str
    calories: int
    meal_category: str = "Snack"
    eaten_date: Optional[date] = None  # defaults to today in crud


class FoodLogUpdate(BaseModel):
    food_name: str
    calories: int
    meal_category: str


class FoodLogRead(BaseModel):
    id: int
    user_id: int
    food_name: str
    calories: int
    meal_category: str
    eaten_date: date
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyCalorieGoalRead(BaseModel):
    user_id: int
    daily_goal: int

    class Config:
        from_attributes = True


class DailyCalorieGoalUpdate(BaseModel):
    daily_goal: int


class DailySummary(BaseModel):
    date: date
    total_calories: int
    goal: int
    entries: List[FoodLogRead]