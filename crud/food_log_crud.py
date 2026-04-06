from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.models import FoodLog, ExerciseLog, DailySetup
from schema.food_log_schema import FoodLogCreate, FoodLogUpdate, ExerciseLogCreate
from schema.food_log_schema import DailySetupCreate, DailySetupUpdate
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


##Daily setup section

async def get_daily_setup(
    session: AsyncSession,
    user_id: int,
    setup_date: str
) -> Optional[DailySetup]:
    """Get daily setup for a specific date"""
    stmt = select(DailySetup).where(
        DailySetup.user_id == user_id,
        DailySetup.setup_date == setup_date
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_daily_setup(
    session: AsyncSession,
    user_id: int,
    setup_date: str,
    data: DailySetupCreate
) -> DailySetup:
    """Create a new daily setup entry"""
    setup = DailySetup(
        user_id=user_id,
        setup_date=setup_date,
        weight=data.weight if hasattr(data, 'weight') and data.weight else 0,
        urine_amount=data.urine_amount if hasattr(data, 'urineAmount') else None
    )
    session.add(setup)
    await session.commit()
    await session.refresh(setup)
    return setup

async def update_daily_setup(
    session: AsyncSession,
    user_id: int,
    setup_date: str,
    data: DailySetupUpdate
) -> DailySetup:
    """Update or create daily setup for a specific date"""
    # Try to get existing setup
    setup = await get_daily_setup(session, user_id, setup_date)
    print("hello")
    if setup:
        # Update existing
        if data.weight is not None:
            setup.weight = data.weight
        if data.urine_amount is not None:
            setup.urine_amount = data.urine_amount
        await session.commit()
        await session.refresh(setup)
        return setup
    else:
        # Create new
        setup = DailySetup(
            user_id=user_id,
            setup_date=setup_date,
            weight=data.weight if data.weight is not None else 0,
            urine_amount=data.urine_amount
        )
        session.add(setup)
        await session.commit()
        await session.refresh(setup)
        return setup