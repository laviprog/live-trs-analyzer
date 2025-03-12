from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.database.models import Role
from src.database.repositories import UserRepository

router = Router()


@router.message(CommandStart())
async def start_command(sender: types.Message):
    telegram_id = sender.from_user.id
    username = sender.from_user.username

    if not await UserRepository.get_user(telegram_id=telegram_id):
        await UserRepository.create_user(username=username, telegram_id=telegram_id)

    await sender.answer(
        f"Hello, your telegram_id: <code>{telegram_id}</code>!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Войти в админку"),
                ]
            ],
            resize_keyboard=True,
        )
    )


@router.message(F.text == "Войти в админку")
@router.message(Command("admin"))
async def admin_command(sender: types.Message):
    telegram_id = sender.from_user.id
    user = await UserRepository.get_user(telegram_id=telegram_id)

    if user.role == Role.ADMIN:
        await sender.answer(
            "Вы успешно вошли в админку!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Каналы"),
                        KeyboardButton(text="Добавить канал"),
                        KeyboardButton(text="Начать анализировать поток"),
                    ]
                ],
                resize_keyboard=True,
            )
        )
    else:
        await sender.answer("К сожалению, у вас нет прав администратора. Нажмите на /help, чтобы узнать подробности")


@router.message(Command("help"))
async def help_command(sender: types.Message):
    await sender.answer("Свяжитесь с @laviprog")
