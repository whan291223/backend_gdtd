from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from core.db import get_session
from crud.spent_naf_crud import (
    create_spent_session,
    update_naf_answers,
    get_test_record,
    get_history_by_user_id,
    delete_session_by_id,
)
from crud.crud_user import get_user_by_line_id
from schema.spent_naf_schema import (
    SpentSubmit, SpentSubmitResponse,
    NafSubmit, NafSubmitResponse,
    SpentNafScoreRead,
)

router = APIRouter(prefix="/test", tags=["test"])


async def get_user_id_or_404(lineUserId: str, session: AsyncSession) -> int:
    """Resolve line_user_id → internal user.id, raise 404 if not found."""
    user = await get_user_by_line_id(session, lineUserId)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{lineUserId}' not found")
    return user.id


@router.post("/spent/{lineUserId}", response_model=SpentSubmitResponse)
async def submit_spent(
    lineUserId: str,
    payload: SpentSubmit,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)

    score = sum(payload.answers)
    is_high_risk = score >= 2          # SPENT threshold: 2+ YES answers

    record = await create_spent_session(
        session, user_id, payload.answers, score, is_high_risk
    )
    return SpentSubmitResponse(
        session_id=record.id,
        spent_score=record.spent_score,
        is_high_risk=record.is_high_risk,
        status=record.status,
    )


@router.put("/naf/{testSessionId}", response_model=NafSubmitResponse)
async def submit_naf(
    testSessionId: int,
    payload: NafSubmit,
    session: AsyncSession = Depends(get_session),
):
    record = await get_test_record(session, testSessionId)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    if not record.is_high_risk:
        raise HTTPException(status_code=400, detail="User is not high risk, NAF not required")
    if record.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    naf_score = sum(payload.answers)

    record = await update_naf_answers(session, record, payload.answers, naf_score)
    return NafSubmitResponse(
        session_id=record.id,
        naf_score=record.naf_score,
        status=record.status,
    )


@router.get("/session/{testSessionId}", response_model=SpentNafScoreRead)
async def get_test_record_by_id(
    testSessionId: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_test_record(db, testSessionId)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return record


@router.get("/history/{lineUserId}", response_model=List[SpentNafScoreRead])
async def get_history(
    lineUserId: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await get_history_by_user_id(session, user_id)


@router.delete("/session/{testSessionId}", status_code=204)
async def delete_session(
    testSessionId: int,
    session: AsyncSession = Depends(get_session),
):
    record = await get_test_record(session, testSessionId)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    await delete_session_by_id(session, record)