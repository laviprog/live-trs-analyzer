import os
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings
from src.database.models import Model, User, Role

logger = logging.getLogger(__name__)

os.makedirs("data", exist_ok=True)

engine = create_async_engine("sqlite+aiosqlite:///data/users.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    async with new_session() as session:
        admin_exists = await session.get(User, 1)
        if not admin_exists:
            default_admin = User(
                telegram_id=settings.ADMIN_TELEGRAM_ID,
                username=settings.ADMIN_USERNAME,
                role=Role.ADMIN
            )
            session.add(default_admin)
            await session.commit()


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
