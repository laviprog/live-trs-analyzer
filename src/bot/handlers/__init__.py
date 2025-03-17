import logging

from aiogram import Dispatcher
from src.bot.handlers.commands import router as commands_router
from src.bot.handlers.channels import router as channels_router
from src.bot.handlers.trs import router as trs_router
from src.model.requests import get_models

logger = logging.getLogger(__name__)

MODELS = get_models()


def register_handlers(dp: Dispatcher):
    dp.include_router(commands_router)
    dp.include_router(channels_router)
    dp.include_router(trs_router)
