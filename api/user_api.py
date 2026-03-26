from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from schema.user_schema import UserCreate, UserUpdate
from crud.crud_user import get_user_by_line_id, create_user, update_user_profile
from core.db import get_session
from fastapi.responses import JSONResponse
from core.config import settings

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/liffId")
async def get_liff_id():
    return JSONResponse({"liffId": settings.LIFF_ID})

@router.post("/createUserProfile")
async def create_user_profile(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_line_id(session, user_data.line_user_id)

    if not user:
        user = await create_user(session, user_data)

    return user

@router.get("/{lineUserId}")
async def get_user_profile(lineUserId: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_line_id(session, lineUserId)
    return user


@router.put("/{lineUserId}")
async def update_user(
    lineUserId: str,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    user = await get_user_by_line_id(session, lineUserId)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await update_user_profile(session, user, user_update)
