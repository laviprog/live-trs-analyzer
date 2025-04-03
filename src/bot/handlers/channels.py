from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.database.repositories import ChannelRepository

router = Router()


class ChannelState(StatesGroup):
    channel = State()


@router.message(F.text == "Каналы")
async def get_channels(sender: types.Message, is_admin: bool):
    if not is_admin:
        await sender.answer("К сожалению, у вас нет прав, чтобы получить список каналов!")
        return

    channels = await ChannelRepository.get_channels_by_user(sender.from_user.id)

    if not channels:
        await sender.answer("У вас нет добавленных каналов.")
        return

    await sender.answer("Список добавленных каналы:")
    for channel in channels:
        await sender.answer(f"Канал: {channel.title}")


@router.message(F.text == "Добавить канал")
async def add_channel(sender: types.Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await sender.answer("К сожалению, у вас нет прав, чтобы добавить канал!")
        return

    await sender.answer("Введите название канала (@channel_name) или ID канала",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChannelState.channel)


@router.message(ChannelState.channel)
async def process_channel_name(message: types.Message, state: FSMContext):
    channel = message.text.strip()

    try:
        chat = await message.bot.get_chat(channel)

        if chat.type == "channel":
            if await ChannelRepository.get_channel(chat.id):
                await message.answer(
                    "Этот канал уже добавлен.",
                    reply_markup=ReplyKeyboardMarkup(
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
                )
                await state.clear()
            else:
                await ChannelRepository.create_channel(chat.id, message.from_user.id, chat.title)
                await message.answer(
                    f"Вы добавили канал: {chat.title}, ID: <code>{chat.id}</code>\n"
                    f"Добавьте бота в этот канал и дайте права администратора, чтобы он мог отправлять результаты аналитики.",
                    reply_markup=ReplyKeyboardMarkup(
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
                )
                await state.clear()
        else:
            await message.answer("Это не канал. Пожалуйста, введите правильное название канала.")

    except Exception as e:
        await message.answer("Канал с такими данными не найден, убедитесь, что вы ввели правильные данные.")
