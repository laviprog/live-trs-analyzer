import asyncio

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from src.bot.handlers import MODELS
from src.process_flow.listener import start_listen

router = Router()

task: asyncio.Task | None = None


class StartState(StatesGroup):
    flow = State()
    key_words = State()
    model = State()


@router.message(F.text == "Начать анализировать поток")
async def start_trs(sender: types.Message, state: FSMContext):
    await sender.answer("Введите поток:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartState.flow)


@router.message(StartState.flow)
async def process_flow(message: types.Message, state: FSMContext):
    flow = message.text.strip()
    await state.update_data(flow=flow)

    await message.answer("Введите ключевые слова через запятую:")
    await state.set_state(StartState.key_words)


@router.message(StartState.key_words)
async def process_key_words(message: types.Message, state: FSMContext):
    key_words = message.text.strip()
    await state.update_data(key_words=key_words)

    await message.answer(
        "Выберите модель для анализа:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=model) for model in MODELS]],
            resize_keyboard=True,
        )
    )
    await state.set_state(StartState.model)



@router.message(StartState.model)
async def process_key_words(message: types.Message, state: FSMContext):
    model = message.text.strip()
    await state.update_data(model=model)

    data = await state.get_data()
    await message.answer(f"Поток: {data['flow']}, ключевые слова: {data['key_words']}, модель: {data['model']}")

    global task
    task = asyncio.create_task(start_listen(flow=data["flow"], key_words=data["key_words"], model=model))

    await message.answer(
        "Анализ начался...",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Закончить анализ"),
                ]
            ],
            resize_keyboard=True,
        )
    )

    await state.clear()


@router.message(F.text == "Закончить анализ")
async def end_trs(sender: types.Message):
    global task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    await sender.answer(
        "Анализ завершен.",
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
