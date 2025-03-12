from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()


@router.message(CommandStart())
async def start_command(sender: types.Message):
    telegram_id = sender.from_user.id
    await sender.answer(f"Hello, your telegram_id: <code>{telegram_id}</code>!")