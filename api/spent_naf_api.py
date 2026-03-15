from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from core.db import get_session
from crud.spent_naf_crud import (
    create_spent_session,
    update_naf_answers,
    get_test_record,          # ← renamed
    get_history_by_user_id,
    delete_session_by_id,
)
from schema.spent_naf_schema import (
    SpentSubmit, SpentSubmitResponse,
    NafSubmit, NafSubmitResponse,
    SpentNafScoreRead,
)

router = APIRouter(prefix="/test", tags=["test"])

@router.post("/spent", response_model=SpentSubmitResponse)
async def submit_spent(
    payload: SpentSubmit,
    session: AsyncSession = Depends(get_session)
):
    score = sum(payload.answers)        # swap with your real scoring logic
    is_high_risk = score >= 6          # swap with your real threshold
    print(score, is_high_risk)
    record = await create_spent_session(
        session, payload.user_id, payload.answers, score, is_high_risk
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
    payload: NafSubmit,
    session: AsyncSession = Depends(get_session)
):
    record = await get_test_record(session, test_session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    if not record.is_high_risk:
        raise HTTPException(status_code=400, detail="User is not high risk, NAF not required")
    if record.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    naf_score = sum(payload.answers)    # swap with your real scoring logic

    record = await update_naf_answers(session, record, payload.answers, naf_score)
    return NafSubmitResponse(
        test_session_id=record.id,
        naf_score=record.naf_score,
        status=record.status,
    )


@router.get("/session/{test_session_id}", response_model=SpentNafScoreRead)
async def get_test_record_by_id(           # ← renamed endpoint function
    test_session_id: int,
    db: AsyncSession = Depends(get_session)  # ← db instead of session
):
    record = await get_test_record(db, test_session_id)  # ← renamed crud call
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return record


@router.get("/history/{user_id}", response_model=List[SpentNafScoreRead])
async def get_history(user_id: int, session: AsyncSession = Depends(get_session)):
    return await get_history_by_user_id(session, user_id)


@router.delete("/session/{test_session_id}", status_code=204)
async def delete_session(
    test_session_id: int,
    session: AsyncSession = Depends(get_session)
):
    record = await get_test_record(session, test_session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    await delete_session_by_id(session, record)

# The folder structure should look like this:
# ```
# ├── api/
# │   └── test_router.py       ← only HTTP logic, thin
# ├── crud/
# │   └── spent_naf_crud.py    ← all DB operations live here
# ├── schema/
# │   └── spent_naf_schema.py  ← pydantic in/out shapes
# ├── models/
# │   └── spent_naf_model.py   ← your SQLModel table