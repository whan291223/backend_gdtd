from fastapi import APIRouter, Depends, HTTPException, Body
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
    NafAnswers, NafSubmitResponse,
    SpentNafScoreRead,
)
from services.naf_calculator import calculate_naf_score
router = APIRouter(prefix="/test", tags=["test"])


async def get_user_id_or_404(line_user_id: str, session: AsyncSession) -> int:
    """Resolve line_user_id → internal user.id, raise 404 if not found."""
    user = await get_user_by_line_id(session, line_user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{line_user_id}' not found")
    return user.id


@router.post("/spent/{line_user_id}", response_model=SpentSubmitResponse)
async def submit_spent(
    line_user_id: str,
    spent_answer: SpentSubmit,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)

    score = sum(spent_answer.answers)
    is_high_risk = score >= 2          # SPENT threshold: 2+ YES answers

    record = await create_spent_session(
        session, user_id, spent_answer.answers, score, is_high_risk
    )
    return SpentSubmitResponse(
        session_id=record.id,
        spent_score=record.spent_score,
        is_high_risk=record.is_high_risk,
        status=record.status,
    )


@router.put("/naf/{test_session_id}", response_model=NafSubmitResponse)
async def submit_naf(
    test_session_id: int,
    naf_answers: NafAnswers,
    session: AsyncSession = Depends(get_session),
):
    record = await get_test_record(session, test_session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    if not record.is_high_risk:
        raise HTTPException(status_code=400, detail="User is not high risk, NAF not required")
    if record.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    # Calculate score and get breakdown
    naf_score, breakdown = calculate_naf_score(naf_answers)
    
    # Update record with breakdown
    record = await update_naf_answers(
        session, 
        record, 
        naf_answers, 
        naf_score,
        breakdown.model_dump()  # Pass breakdown as dict for JSON storage
    )
    
    return NafSubmitResponse(
        session_id=record.id,
        naf_score=record.naf_score,
        status=record.status,
    )


@router.get("/session/{test_session_id}", response_model=SpentNafScoreRead)
async def get_test_record_by_id(
    test_session_id: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_test_record(db, test_session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return record


@router.get("/history/{line_user_id}", response_model=List[SpentNafScoreRead])
async def get_history(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    return await get_history_by_user_id(session, user_id)


@router.delete("/session/{test_session_id}", status_code=204)
async def delete_session(
    test_session_id: int,
    session: AsyncSession = Depends(get_session),
):
    record = await get_test_record(session, test_session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    await delete_session_by_id(session, record)