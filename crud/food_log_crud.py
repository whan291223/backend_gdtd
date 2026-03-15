from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date, timezone
from model.models import FoodLog, DailyCalorieGoal
from schema.food_log_schema import FoodLogCreate, FoodLogUpdate, DailyCalorieGoalUpdate
from typing import Optional, List

# ── Food log ──────────────────────────────────────────────────────

async def create_food_log(
    db: AsyncSession,
    payload: FoodLogCreate,
) -> FoodLog:
    record = FoodLog(
        user_id=payload.user_id,
        food_name=payload.food_name,
        calories=payload.calories,
        meal_category=payload.meal_category,
        eaten_date=payload.eaten_date or datetime.now(timezone.utc).date(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_food_log_record(
    db: AsyncSession,
    record_id: int,
) -> Optional[FoodLog]:
    return await db.get(FoodLog, record_id)


async def get_food_logs_by_date(
    db: AsyncSession,
    user_id: int,
    target_date: date,
) -> List[FoodLog]:
    result = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id)
        .where(FoodLog.eaten_date == target_date)
        .order_by(FoodLog.created_at.asc())
    )
    return result.scalars().all()


async def get_all_food_logs_by_user(
    db: AsyncSession,
    user_id: int,
) -> List[FoodLog]:
    result = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id)
        .order_by(FoodLog.eaten_date.desc(), FoodLog.created_at.asc())
    )
    return result.scalars().all()


async def update_food_log_record(
    db: AsyncSession,
    record: FoodLog,
    payload: FoodLogUpdate,
) -> FoodLog:
    record.food_name = payload.food_name
    record.calories = payload.calories
    record.meal_category = payload.meal_category
    await db.commit()
    await db.refresh(record)
    return record


async def delete_food_log_record(
    db: AsyncSession,
    record: FoodLog,
) -> None:
    await db.delete(record)
    await db.commit()


# ── Calorie goal ──────────────────────────────────────────────────

async def get_calorie_goal(
    db: AsyncSession,
    user_id: int,
) -> Optional[DailyCalorieGoal]:
    result = await db.execute(
        select(DailyCalorieGoal).where(DailyCalorieGoal.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_calorie_goal(
    db: AsyncSession,
    user_id: int,
    payload: DailyCalorieGoalUpdate,
) -> DailyCalorieGoal:
    record = await get_calorie_goal(db, user_id)
    if record:
        record.daily_goal = payload.daily_goal
    else:
        record = DailyCalorieGoal(user_id=user_id, daily_goal=payload.daily_goal)
        db.add(record)
    await db.commit()
    await db.refresh(record)
    return record