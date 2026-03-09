from sqlmodel import select
from model.models import User
from schema.user_schema import UserCreate
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_user_by_line_id(session: AsyncSession, line_user_id: str):
    statement = select(User).where(User.line_user_id == line_user_id)
    result = await session.exec(statement)
    return result.first()


async def create_user(session: AsyncSession, user_data: UserCreate):
    user = User(**user_data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_real_name(session: AsyncSession, user: User, real_name: str):
    user.real_name = real_name
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user