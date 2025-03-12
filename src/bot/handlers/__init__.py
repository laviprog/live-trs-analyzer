import logging

from aiogram import Dispatcher
from src.bot.handlers.commands import router as commands_router
from src.bot.handlers.channels import router as channels_router

logger = logging.getLogger(__name__)


def register_handlers(dp: Dispatcher):
    dp.include_router(commands_router)
    dp.include_router(channels_router)
