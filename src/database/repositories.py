from sqlalchemy import select

from src.database import new_session
from src.database.models import Role, User, Channel


class UserRepository:
    @classmethod
    async def create_user(
            cls,
            username: str,
            telegram_id: int,
            role: Role = Role.USER
    ) -> User | None:

        async with new_session() as session:
            user = User(username=username, telegram_id=telegram_id, role=role)
            session.add(user)

            await session.commit()
            return user

    @classmethod
    async def get_user(
            cls,
            user_id: int = None,
            telegram_id: int = None,
            username: str = None
    ) -> User | None:

        query = select(User)

        if telegram_id:
            query = query.filter(User.telegram_id == telegram_id)
        elif user_id:
            query = query.filter(User.id == user_id)
        elif username:
            query = query.filter(User.username == username)
        else:
            raise ValueError(
                "You must specify at least one of the following parameters: user_id, telegram_id, username")

        async with new_session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_users(cls) -> list[User]:
        async with new_session() as session:
            result = await session.execute(
                select(User)
            )
            return list(result.scalars().all())


class ChannelRepository:
    @classmethod
    async def create_channel(
            cls,
            channel_id: int,
            user_id: int,
            title: str
    ) -> Channel | None:
        async with new_session() as session:
            channel = Channel(channel_id=channel_id, user_id=user_id, title=title)
            session.add(channel)

            await session.commit()
            return channel

    @classmethod
    async def get_channel(
            cls,
            channel_id: int
    ) -> Channel | None:
        async with new_session() as session:
            result = await session.execute(
                select(Channel).filter(Channel.channel_id == channel_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def get_channels(cls) -> list[Channel]:
        async with new_session() as session:
            result = await session.execute(
                select(Channel)
            )
            return list(result.scalars().all())

    @classmethod
    async def get_channels_by_user(cls, telegram_id: int) -> list[Channel]:
        async with new_session() as session:
            result = await session.execute(
                select(Channel).filter(Channel.user_id == telegram_id)
            )
            return list(result.scalars().all())
