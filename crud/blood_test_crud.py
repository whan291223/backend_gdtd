from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.models import BloodTest
from schema.blood_test_schema import BloodTestCreate
from typing import Optional, List

async def create_blood_test(
    session: AsyncSession,
    user_id: int,
    data: BloodTestCreate,
) -> BloodTest:
    record = BloodTest(user_id=user_id, **data.model_dump())
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_latest_blood_test(
    session: AsyncSession,
    user_id: int,
) -> Optional[BloodTest]:
    result = await session.execute(
        select(BloodTest)
        .where(BloodTest.user_id == user_id)
        .order_by(BloodTest.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_blood_test_history(
    session: AsyncSession,
    user_id: int,
) -> List[BloodTest]:
    result = await session.execute(
        select(BloodTest)
        .where(BloodTest.user_id == user_id)
        .order_by(BloodTest.recorded_at.desc())
    )
    return list(result.scalars().all())