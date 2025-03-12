import os
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.database.models import Model

logger = logging.getLogger(__name__)

os.makedirs("data", exist_ok=True)

engine = create_async_engine("sqlite+aiosqlite:///data/users.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
