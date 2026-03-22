from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.models import FoodLog, ExerciseLog, DailyCalorieGoal
from schema.food_log_schema import FoodLogCreate, FoodLogUpdate, ExerciseLogCreate, DailyCalorieGoalUpdate
from typing import List, Optional

# --- Food Log ----------------------------------------------------------------

async def add_food_log(session: AsyncSession, user_id: int, data: FoodLogCreate) -> FoodLog:
    entry = FoodLog(user_id=user_id, **data.model_dump())
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_food_logs_by_date(session: AsyncSession, user_id: int, date: str) -> List[FoodLog]:
    result = await session.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id, FoodLog.eaten_date == date)
        .order_by(FoodLog.created_at)
    )
    return list(result.scalars().all())


async def delete_food_log(session: AsyncSession, entry_id: int, user_id: int) -> bool:
    result = await session.execute(
        select(FoodLog).where(FoodLog.id == entry_id, FoodLog.user_id == user_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        return False
    await session.delete(entry)
    await session.commit()
    return True


# --- Exercise Log ------------------------------------------------------------

async def add_exercise_log(session: AsyncSession, user_id: int, data: ExerciseLogCreate) -> ExerciseLog:
    entry = ExerciseLog(user_id=user_id, **data.model_dump())
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def get_exercise_logs_by_date(session: AsyncSession, user_id: int, date: str) -> List[ExerciseLog]:
    result = await session.execute(
        select(ExerciseLog)
        .where(ExerciseLog.user_id == user_id, ExerciseLog.logged_date == date)
        .order_by(ExerciseLog.created_at)
    )
    return list(result.scalars().all())


async def delete_exercise_log(session: AsyncSession, entry_id: int, user_id: int) -> bool:
    result = await session.execute(
        select(ExerciseLog).where(ExerciseLog.id == entry_id, ExerciseLog.user_id == user_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        return False
    await session.delete(entry)
    await session.commit()
    return True


# --- Daily Calorie Goal ------------------------------------------------------

async def get_or_create_calorie_goal(session: AsyncSession, user_id: int) -> DailyCalorieGoal:
    result = await session.execute(
        select(DailyCalorieGoal).where(DailyCalorieGoal.user_id == user_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        goal = DailyCalorieGoal(user_id=user_id, daily_goal=2000)
        session.add(goal)
        await session.commit()
        await session.refresh(goal)
    return goal


async def update_calorie_goal(
    session: AsyncSession, user_id: int, data: DailyCalorieGoalUpdate
) -> DailyCalorieGoal:
    goal = await get_or_create_calorie_goal(session, user_id)
    goal.daily_goal = data.daily_goal
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal


async def update_food_log(
    session: AsyncSession,
    entry_id: int,
    user_id: int,
    data: FoodLogUpdate,
) -> Optional[FoodLog]:
    from sqlmodel import select
    result = await session.execute(
        select(FoodLog).where(FoodLog.id == entry_id, FoodLog.user_id == user_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry