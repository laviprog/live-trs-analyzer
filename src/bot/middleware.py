from aiogram.types import Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from src.database.models import Role
from src.database.repositories import UserRepository


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user = await UserRepository.get_user(username=event.message.from_user.username)
        data['is_admin'] = user is not None and user.role == Role.ADMIN
        return await handler(event, data)
