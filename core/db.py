from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionFactory = sessionmaker( # use session for query, add newdata, savechanges
    engine,
    class_ = AsyncSession,
    expire_on_commit=False #after commit data still available even the session is expire
)

async def get_session(): # using async and await mean that if there is paralell work they can start like away
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback() # remove all changes and go to zero
            raise
        finally:
            await session.close()