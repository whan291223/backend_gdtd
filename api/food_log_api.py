from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_session
from crud.crud_user import get_user_by_line_id
from crud.food_log_crud import (
    update_food_log,
    add_food_log, get_food_logs_by_date, delete_food_log,
    add_exercise_log, get_exercise_logs_by_date, delete_exercise_log,
    get_or_create_calorie_goal, update_calorie_goal,
)
from schema.food_log_schema import (
    FoodLogUpdate,
    FoodLogCreate, FoodLogRead,
    ExerciseLogCreate, ExerciseLogRead,
    DailyCalorieGoalRead, DailyCalorieGoalUpdate,
)

router = APIRouter(prefix="/foodLog", tags=["FoodLog"])


async def get_user_id_or_404(lineUserId: str, session: AsyncSession) -> int:
    user = await get_user_by_line_id(session, lineUserId)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{lineUserId}' not found")
    return user.id


# --- Food entries ------------------------------------------------------------

@router.post("/{lineUserId}/food", response_model=FoodLogRead)
async def log_food(
    lineUserId: str,
    data: FoodLogCreate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await add_food_log(session, user_id, data)


@router.get("/{lineUserId}/food/{date}", response_model=List[FoodLogRead])
async def get_food_by_date(
    lineUserId: str,
    date: str,  # YYYY-MM-DD
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await get_food_logs_by_date(session, user_id, date)


@router.put("/{lineUserId}/food/{entryId}", response_model=FoodLogRead)
async def edit_food(
    lineUserId: str,
    entryId: int,
    data: FoodLogUpdate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    entry = await update_food_log(session, entryId, user_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    return entry


@router.delete("/{lineUserId}/food/{entryId}", status_code=204)
async def remove_food(
    lineUserId: str,
    entryId: int,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    deleted = await delete_food_log(session, entryId, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Food entry not found")


# --- Exercise entries --------------------------------------------------------

@router.post("/{lineUserId}/exercise", response_model=ExerciseLogRead)
async def log_exercise(
    lineUserId: str,
    data: ExerciseLogCreate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await add_exercise_log(session, user_id, data)


@router.get("/{lineUserId}/exercise/{date}", response_model=List[ExerciseLogRead])
async def get_exercise_by_date(
    lineUserId: str,
    date: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await get_exercise_logs_by_date(session, user_id, date)


@router.delete("/{lineUserId}/exercise/{entryId}", status_code=204)
async def remove_exercise(
    lineUserId: str,
    entryId: int,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    deleted = await delete_exercise_log(session, entryId, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercise entry not found")


# --- Calorie goal ------------------------------------------------------------

@router.get("/{lineUserId}/goal", response_model=DailyCalorieGoalRead)
async def get_goal(
    lineUserId: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await get_or_create_calorie_goal(session, user_id)


@router.put("/{lineUserId}/goal", response_model=DailyCalorieGoalRead)
async def set_goal(
    lineUserId: str,
    data: DailyCalorieGoalUpdate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await update_calorie_goal(session, user_id, data)