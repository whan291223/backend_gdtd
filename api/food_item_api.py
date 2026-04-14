from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from pydantic import BaseModel
from core.db import get_session
from model.models import FoodDatabase, ExerciseDatabase
from schema.food_log_schema import ExerciseItem, FoodItem

router = APIRouter(prefix="/food-exercise", tags=["FoodExercise"])

@router.get("/foods", response_model=List[FoodItem])
async def get_foods(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(FoodDatabase).order_by(FoodDatabase.name))
    return result.scalars().all()


@router.get("/exercises", response_model=List[ExerciseItem])
async def get_exercises(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ExerciseDatabase).order_by(ExerciseDatabase.name))
    return result.scalars().all()
