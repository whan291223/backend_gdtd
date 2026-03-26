from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_session
from crud.crud_user import get_user_by_line_id
from crud.blood_test_crud import (
    get_latest_blood_test,
    get_blood_test_history,
)
from schema.blood_test_schema import BloodTestCreate, BloodTestRead

router = APIRouter(prefix="/bloodTest", tags=["BloodTest"])


async def get_user_id_or_404(lineUserId: str, session: AsyncSession) -> int:
    user = await get_user_by_line_id(session, lineUserId)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{lineUserId}' not found")
    return user.id


# GET latest — for pre-filling the form
@router.get("/{lineUserId}/latest", response_model=BloodTestRead)
async def read_latest(
    lineUserId: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    record = await get_latest_blood_test(session, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="No blood test records found")
    return record


# GET history — all past records
@router.get("/{lineUserId}/history", response_model=List[BloodTestRead])
async def read_history(
    lineUserId: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(lineUserId, session)
    return await get_blood_test_history(session, user_id)