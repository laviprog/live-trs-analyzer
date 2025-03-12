from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.repositories import ChannelRepository

router = Router()

class ChannelState(StatesGroup):
    channel = State()

@router.message(F.text == "Каналы")
async def get_channels(sender: types.Message):
    channels = await ChannelRepository.get_channels_by_user(sender.from_user.id)

    if not channels:
        await sender.answer("У вас нет добавленных каналов.")
        return

    for channel in channels:
        await sender.answer(f"Канал: {channel.title}")

@router.message(F.text == "Добавить канал")
async def add_channel(sender: types.Message, state: FSMContext):
    await sender.answer("Введите название канала (@channel_name) или ID канала")
    await state.set_state(ChannelState.channel)


@router.message(ChannelState.channel)
async def process_channel_name(message: types.Message, state: FSMContext):
    channel = message.text.strip()

    try:
        chat = await message.bot.get_chat(channel)

        if chat.type == "channel":
            if await ChannelRepository.get_channel(chat.id):
                await message.answer("Этот канал уже добавлен.")
            else:
                await ChannelRepository.create_channel(chat.id, message.from_user.id, chat.title)
                await message.answer(f"Вы добавили канал: {chat.title}, ID: <code>{chat.id}</code>")
        else:
            await message.answer("Это не канал. Пожалуйста, введите правильное название канала.")

    except Exception as e:
        await message.answer("Канал с такими данными не найден, убедитесь, что вы ввели правильные данные.")

    await state.clear()
