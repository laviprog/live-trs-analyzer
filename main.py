import asyncio

from src.bot import start_bot
from src.database import create_tables


async def main():
    await create_tables()
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
