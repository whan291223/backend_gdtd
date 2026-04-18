from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from schema.user_schema import UserCreate, UserUpdate
from crud.crud_user import get_user_by_line_id, create_user, update_user_profile
from core.db import get_session
from fastapi.responses import JSONResponse
from core.config import settings
from core.auth import verify_line_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/liff-id")
async def get_liff_id():
    return JSONResponse({"liffId": settings.LIFF_ID})

@router.post("/create_user_profile")
async def create_user_profile(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    verified_line_id: str = Depends(verify_line_user)
):
    if user_data.line_user_id != verified_line_id:
        raise HTTPException(status_code=403, detail="Line ID mismatch")

    user = await get_user_by_line_id(session, user_data.line_user_id)

    if not user:
        user = await create_user(session, user_data)

    return user

@router.get("/{line_user_id}")
async def get_user_profile(
    line_user_id: str,
    session: AsyncSession = Depends(get_session),
    verified_line_id: str = Depends(verify_line_user)
):
    if line_user_id != verified_line_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = await get_user_by_line_id(session, line_user_id)
    return user


@router.put("/{line_user_id}")
async def update_user(
    line_user_id: str,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_session),
    verified_line_id: str = Depends(verify_line_user)
):
    if line_user_id != verified_line_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = await get_user_by_line_id(session, line_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await update_user_profile(session, user, user_update)
