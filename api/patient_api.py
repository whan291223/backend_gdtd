from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session

from schema.patient_schema import (
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileRead,
)
from crud.patient_crud import (
    create_patient_profile,
    get_patient_profile,
    update_patient_profile,
    delete_patient_profile,
)
from crud.crud_user import get_user_by_line_id

router = APIRouter(prefix="/patient-profile", tags=["PatientProfile"])


async def get_user_id_or_404(line_user_id: str, session: AsyncSession) -> int:
    """Resolve line_user_id → internal user.id, raise 404 if not found."""
    user = await get_user_by_line_id(session, line_user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{line_user_id}' not found")
    return user.id


# 👉 CREATE
@router.post("/{line_user_id}", response_model=PatientProfileRead)
async def create_profile(
    line_user_id: str,
    data: PatientProfileCreate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)

    # Prevent duplicate profiles
    existing = await get_patient_profile(session, user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Profile already exists, use PUT to update")

    return await create_patient_profile(session, user_id, data)


# 👉 READ
@router.get("/{line_user_id}", response_model=PatientProfileRead)
async def read_profile(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    profile = await get_patient_profile(session, user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# 👉 UPDATE
@router.put("/{line_user_id}", response_model=PatientProfileRead)
async def update_profile(
    line_user_id: str,
    data: PatientProfileUpdate,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    profile = await get_patient_profile(session, user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return await update_patient_profile(session, profile, data)


# 👉 DELETE
@router.delete("/{line_user_id}")
async def delete_profile(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = await get_user_id_or_404(line_user_id, session)
    profile = await get_patient_profile(session, user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    await delete_patient_profile(session, profile)
    return {"message": "Deleted successfully"}