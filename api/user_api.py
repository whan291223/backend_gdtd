from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from schema.user_schema import UserCreate, UserUpdate
from crud.crud_user import get_user_by_line_id, create_user, update_real_name
from core.db import get_session
from fastapi.responses import JSONResponse
from core.config import settings
import os

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/liff-id")
async def get_liff_id():
    return JSONResponse({"liffId": settings.LIFF_ID})

@router.post("/create_user_profile")
async def create_user_profile(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_line_id(session, user_data.line_user_id)

    if not user:
        user = await create_user(session, user_data)

    return user

@router.get("/{line_user_id}")
async def get_user_profile(line_user_id: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_line_id(session, line_user_id)
    return user

@router.get("/{line_user_id}")
async def is_already_in_database(line_user_id: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_line_id(session, line_user_id)
    if user:
        return True
    return False

@router.put("/{line_user_id}")
async def update_user(
    line_user_id: str,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    user = await get_user_by_line_id(session, line_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await update_real_name(session, user, user_update.real_name)
