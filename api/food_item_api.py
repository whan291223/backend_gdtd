from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from pydantic import BaseModel
from core.db import get_session
from model.models import FoodDatabase

router = APIRouter(prefix="/api", tags=["foods"])


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