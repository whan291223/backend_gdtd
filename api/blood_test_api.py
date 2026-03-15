from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.db import get_session
from crud.blood_test_crud import (
    create_blood_test,
    get_blood_test_record,
    get_blood_tests_by_user,
    update_blood_test_record,
    delete_blood_test_record,
)
from schema.blood_test_schema import BloodTestCreate, BloodTestUpdate, BloodTestRead

router = APIRouter(prefix="/blood-test", tags=["blood-test"])


# ── CREATE ────────────────────────────────────────────────────────
@router.post("", response_model=BloodTestRead)
async def add_blood_test(
    payload: BloodTestCreate,
    db: AsyncSession = Depends(get_session),
):
    return await create_blood_test(db, payload)


# ── READ: all records for a user ──────────────────────────────────
@router.get("/history/{user_id}", response_model=List[BloodTestRead])
async def get_blood_test_history(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    return await get_blood_tests_by_user(db, user_id)


# ── READ: single record ───────────────────────────────────────────
@router.get("/{record_id}", response_model=BloodTestRead)
async def get_blood_test(
    record_id: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_blood_test_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ── UPDATE ────────────────────────────────────────────────────────
@router.put("/{record_id}", response_model=BloodTestRead)
async def update_blood_test(
    record_id: int,
    payload: BloodTestUpdate,
    db: AsyncSession = Depends(get_session),
):
    record = await get_blood_test_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return await update_blood_test_record(db, record, payload)


# ── DELETE ────────────────────────────────────────────────────────
@router.delete("/{record_id}", status_code=204)
async def delete_blood_test(
    record_id: int,
    db: AsyncSession = Depends(get_session),
):
    record = await get_blood_test_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    await delete_blood_test_record(db, record)