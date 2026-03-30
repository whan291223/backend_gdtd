from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model.models import SpentNafScore
from typing import List, Optional

async def create_spent_session(
    session: AsyncSession,
    user_id: int,
    answers: List[int],
    score: int,
    is_high_risk: bool,
) -> SpentNafScore:
    record = SpentNafScore(
        user_id=user_id,
        user_answer_spent=answers,
        spent_score=score,
        is_high_risk=is_high_risk,
        status="pending_naf" if is_high_risk else "skipped_naf",
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def update_naf_answers(
    session: AsyncSession,
    record: SpentNafScore,
    answers: List[int],
    score: int,
) -> SpentNafScore:
    # record.user_answer_naf = answers
    record.naf_score = score
    record.status = "completed"
    await session.commit()
    await session.refresh(record)
    return record


async def get_test_record(
    session: AsyncSession,
    session_id: int,
) -> Optional[SpentNafScore]:
    return await session.get(SpentNafScore, session_id)


async def get_history_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> List[SpentNafScore]:
    result = await session.execute(
        select(SpentNafScore)
        .where(SpentNafScore.user_id == user_id)
        .order_by(SpentNafScore.submitted_at.desc())
    )
    return result.scalars().all()


async def delete_session_by_id(
    session: AsyncSession,
    record: SpentNafScore,
) -> None:
    await session.delete(record)
    await session.commit()