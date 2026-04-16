from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_session
from crud.crud_user import get_user_by_line_id
from core.auth import verify_line_user
from crud.blood_test_crud import (
    get_latest_blood_test,
    get_blood_test_history,
)
from schema.blood_test_schema import BloodTestCreate, BloodTestRead

router = APIRouter(prefix="/blood-test", tags=["BloodTest"])


async def get_user_id_or_404(line_user_id: str, session: AsyncSession) -> int:
    user = await get_user_by_line_id(session, line_user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{line_user_id}' not found")
    return user.id


# GET latest — for pre-filling the form
@router.get("/{line_user_id}/latest", response_model=BloodTestRead)
async def read_latest(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
    verified_line_id: str = Depends(verify_line_user)
):
    if line_user_id != verified_line_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user_id = await get_user_id_or_404(line_user_id, session)
    record = await get_latest_blood_test(session, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="No blood test records found")
    return record


# GET history — all past records
@router.get("/{line_user_id}/history", response_model=List[BloodTestRead])
async def read_history(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
    verified_line_id: str = Depends(verify_line_user)
):
    if line_user_id != verified_line_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user_id = await get_user_id_or_404(line_user_id, session)
    return await get_blood_test_history(session, user_id)