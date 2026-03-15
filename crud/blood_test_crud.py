from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model.models import BloodTest
from schema.blood_test_schema import BloodTestCreate, BloodTestUpdate
from typing import Optional, List

async def create_blood_test(
    db: AsyncSession,
    payload: BloodTestCreate,
) -> BloodTest:
    record = BloodTest(
        user_id=payload.user_id,
        blood_level=payload.blood_level,
        note=payload.note,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_blood_test_record(
    db: AsyncSession,
    record_id: int,
) -> Optional[BloodTest]:
    return await db.get(BloodTest, record_id)


async def get_blood_tests_by_user(
    db: AsyncSession,
    user_id: int,
) -> List[BloodTest]:
    result = await db.execute(
        select(BloodTest)
        .where(BloodTest.user_id == user_id)
        .order_by(BloodTest.recorded_at.desc())
    )
    return result.scalars().all()


async def update_blood_test_record(
    db: AsyncSession,
    record: BloodTest,
    payload: BloodTestUpdate,
) -> BloodTest:
    record.blood_level = payload.blood_level
    record.note = payload.note
    await db.commit()
    await db.refresh(record)
    return record


async def delete_blood_test_record(
    db: AsyncSession,
    record: BloodTest,
) -> None:
    await db.delete(record)
    await db.commit()