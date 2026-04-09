from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from pydantic import BaseModel
from core.db import get_session
from model.models import FoodDatabase, ExerciseDatabase

router = APIRouter(prefix="/api", tags=["foods"])


class ExerciseItem(BaseModel):
    id: int
    name: str
    met: float


class FoodItem(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float


@router.get("/foods", response_model=List[FoodItem])
async def get_foods(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(FoodDatabase).order_by(FoodDatabase.name))
    return result.scalars().all()


@router.get("/exercises", response_model=List[ExerciseItem])
async def get_exercises(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ExerciseDatabase).order_by(ExerciseDatabase.name))
    return result.scalars().all()
