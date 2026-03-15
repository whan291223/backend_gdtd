from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from core.db import get_session
from crud.food_log_crud import (
    create_food_log,
    get_food_log_record,
    get_food_logs_by_date,
    get_all_food_logs_by_user,
    update_food_log_record,
    delete_food_log_record,
    get_calorie_goal,
    upsert_calorie_goal,
)
from schema.food_log_schema import (
    FoodLogCreate,
    FoodLogUpdate,
    FoodLogRead,
    DailyCalorieGoalRead,
    DailyCalorieGoalUpdate,
    DailySummary,
)

router = APIRouter(prefix="/food", tags=["food"])


# ── Food log CRUD ─────────────────────────────────────────────────

@router.post("", response_model=FoodLogRead)
async def add_food_log(
    payload: FoodLogCreate,
    db: AsyncSession = Depends(get_session),
):
    return await create_food_log(db, payload)


@router.get("/date/{user_id}", response_model=DailySummary)
async def get_food_by_date(
    user_id: int,
    target_date: date,          # query param: ?target_date=2024-01-15
    db: AsyncSession = Depends(get_session),
):
    entries = await get_food_logs_by_date(db, user_id, target_date)
    goal_record = await get_calorie_goal(db, user_id)
    goal = goal_record.daily_goal if goal_record else 2000
    total = sum(e.calories for e in entries)
    return DailySummary(date=target_date, total_calories=total, goal=goal, entries=entries)


@router.get("/history/{user_id}", response_model=List[FoodLogRead])
async def get_all_food_logs(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    return await get_all_food_logs_by_user(db, user_id)


@router.put("/{record_id}", response_model=FoodLogRead)
async def update_food_log(
    record_id: int,
    payload: FoodLogUpdate,
    db: AsyncSession = Depends(get_session),
):
    record = await get_food_log_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Food log not found")
    return await update_food_log_record(db, record, payload)


@router.delete("/{record_id}", status_code=204)
async def delete_food_log(
    record_id: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_food_log_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Food log not found")
    await delete_food_log_record(db, record)


# ── Calorie goal ──────────────────────────────────────────────────

@router.get("/goal/{user_id}", response_model=DailyCalorieGoalRead)
async def get_goal(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_calorie_goal(db, user_id)
    if not record:
        return DailyCalorieGoalRead(user_id=user_id, daily_goal=2000)
    return record


@router.put("/goal/{user_id}", response_model=DailyCalorieGoalRead)
async def set_goal(
    user_id: int,
    payload: DailyCalorieGoalUpdate,
    db: AsyncSession = Depends(get_session),
):
    return await upsert_calorie_goal(db, user_id, payload)