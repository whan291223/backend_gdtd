from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_session
from crud.crud_user import get_user_by_line_id
from crud.food_log_crud import (
    update_food_log,
    add_food_log, get_food_logs_by_date, delete_food_log,
    add_exercise_log, get_exercise_logs_by_date, delete_exercise_log,
    get_daily_setup, update_daily_setup
)

from schema.food_log_schema import (
    FoodLogUpdate,
    FoodLogCreate, FoodLogRead,
    ExerciseLogCreate, ExerciseLogRead,
    DailySetupUpdate, DailySetupRead,
)

router = APIRouter(prefix="/food-log", tags=["FoodLog"])


async def get_user_id_or_404(line_user_id: str, session: AsyncSession) -> int:
    user = await get_user_by_line_id(session, line_user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{line_user_id}' not found")
    return user.id


# --- Daily Setup -------------------------------------------------------------

@router.get("/{line_user_id}/setup/{setup_date}", response_model=DailySetupRead)
async def get_setup_by_date(
    line_user_id: str,
    setup_date: str,  # YYYY-MM-DD
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    setup = await get_daily_setup(session, user_id, setup_date)
    if not setup:
        raise HTTPException(status_code=404, detail="Daily setup not found")
    
    return DailySetupRead(
        weight=setup.weight,
        urine_amountount=setup.urine_amount,
        setup_date=str(setup.setup_date)
    )


@router.put("/{line_user_id}/setup/{setup_date}", response_model=DailySetupRead)
async def update_setup(
    line_user_id: str,
    setup_date: str,  # YYYY-MM-DD
    data: DailySetupUpdate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    setup = await update_daily_setup(session, user_id, setup_date, data)
    
    return DailySetupRead(
        weight=setup.weight,
        urine_amount=setup.urine_amount,
        setup_date=str(setup.setup_date)
    )


# --- Food entries ------------------------------------------------------------

@router.post("/{line_user_id}/food", response_model=FoodLogRead)
async def log_food(
    line_user_id: str,
    data: FoodLogCreate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    return await add_food_log(session, user_id, data)


@router.get("/{line_user_id}/food/{date}", response_model=List[FoodLogRead])
async def get_food_by_date(
    line_user_id: str,
    date: str,  # YYYY-MM-DD
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    return await get_food_logs_by_date(session, user_id, date)


@router.put("/{line_user_id}/food/{entry_id}", response_model=FoodLogRead)
async def edit_food(
    line_user_id: str,
    entry_id: int,
    data: FoodLogUpdate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    entry = await update_food_log(session, entry_id, user_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    return entry


@router.delete("/{line_user_id}/food/{entry_id}", status_code=204)
async def remove_food(
    line_user_id: str,
    entry_id: int,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    deleted = await delete_food_log(session, entry_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Food entry not found")


# --- Exercise entries --------------------------------------------------------

@router.post("/{line_user_id}/exercise", response_model=ExerciseLogRead)
async def log_exercise(
    line_user_id: str,
    data: ExerciseLogCreate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    return await add_exercise_log(session, user_id, data)


@router.get("/{line_user_id}/exercise/{date}", response_model=List[ExerciseLogRead])
async def get_exercise_by_date(
    line_user_id: str,
    date: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    return await get_exercise_logs_by_date(session, user_id, date)


@router.delete("/{line_user_id}/exercise/{entry_id}", status_code=204)
async def remove_exercise(
    line_user_id: str,
    entry_id: int,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    deleted = await delete_exercise_log(session, entry_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exercise entry not found")