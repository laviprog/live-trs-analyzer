from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from src.database import Role
from src.database.repositories import UserRepository

router = Router()


class AdminState(StatesGroup):
    username = State()


@router.message(F.text == "Добавить админа")
async def get_channels(mes: Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await mes.answer("К сожалению, у вас нет прав, чтобы получить список каналов!")
        return

    await mes.answer("Пришлите имя пользователя, которому хотите дать права администратора (например, @username):",
                     reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.username)


@router.message(AdminState.username)
async def username_process(mes: Message, state: FSMContext):
    username = mes.text.strip()

    if username.startswith('@'):
        username = username[1:]
    else:
        await mes.answer("Имя пользователя должно начинаться с @. Попробуйте еще раз.")
        return

    user = await UserRepository.get_user(username=username)
    if user is None:
        user = await UserRepository.create_user(username=username, role=Role.ADMIN)
    else:
        user = await UserRepository.update_user_role(user)

    keyboard = ReplyKeyboardMarkup(
        keyboard=
        [
            [
                KeyboardButton(text="Каналы"),
                KeyboardButton(text="Добавить канал")
            ],
            [
                KeyboardButton(text="Начать анализировать поток"),
                KeyboardButton(text="Добавить админа")
            ]
        ],
        resize_keyboard=True,
    )

    if user is not None and user.role == 'admin':
        await mes.answer(
            f"Пользователь @{username} добавлен в администраторы.",
            keyboard=keyboard
        )
    else:
        await mes.answer(
            f"Не удалось добавить пользователя @{username} в администраторы.",
            keyboard=keyboard
        )

    await state.clear()
