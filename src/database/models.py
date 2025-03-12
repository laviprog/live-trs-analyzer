from enum import Enum

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Model(DeclarativeBase):
    pass


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]
    username: Mapped[str]
    role: Mapped[Role] = mapped_column(String)

    channels: Mapped[list["Channel"]] = relationship(back_populates="user", cascade="all, delete")


class Channel(Model):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int]
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="channels")
