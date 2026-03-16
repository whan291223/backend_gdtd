from sqlmodel import select
from model.models import User
from schema.user_schema import UserCreate, UserUpdate
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


async def update_user_profile(
    db: AsyncSession,
    user: User,                  # the actual user object fetched from DB
    user_update: UserUpdate,     # the pydantic schema with new values
) -> User:
    user.real_name = user_update.real_name
    user.surname = user_update.surname   # ← add surname

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user