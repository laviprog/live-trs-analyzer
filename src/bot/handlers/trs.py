import asyncio

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from src.model.requests import get_models
from src.process_flow.listener import Listener

router = Router()

listener: Listener | None = None


class StartState(StatesGroup):
    flow = State()
    language = State()
    keywords = State()
    model = State()


@router.message(F.text == "Начать анализировать поток")
async def start_trs(sender: types.Message, state: FSMContext, is_admin: bool):
    if not is_admin:
        await sender.answer("К сожалению, у вас нет прав, чтобы начать анализировать поток!")
        return

    await sender.answer("Введите поток:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartState.flow)


@router.message(StartState.flow)
async def process_flow(message: types.Message, state: FSMContext):
    flow = message.text.strip()
    await state.update_data(flow=flow)

    await message.answer(
        'Введите язык (en, ru, kk) или поставьте прочерк "-" (будет использован язык по умолчанию – en):')
    await state.set_state(StartState.language)


@router.message(StartState.language)
async def process_language(message: types.Message, state: FSMContext):
    language = message.text.strip()

    if language == '-':
        language = 'en'

    await state.update_data(language=language)

    await message.answer("Введите ключевые слова через запятую:")
    await state.set_state(StartState.keywords)


@router.message(StartState.keywords)
async def process_key_words(message: types.Message, state: FSMContext):
    keywords = [keyword.strip() for keyword in message.text.strip().split(',')]
    await state.update_data(keywords=keywords)

    await message.answer(
        "Выберите модель для анализа:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=model) for model in await get_models()]],
            resize_keyboard=True,
        )
    )
    await state.set_state(StartState.model)


@router.message(StartState.model)
async def process_model(message: types.Message, state: FSMContext):
    model = message.text.strip()

    data = await state.get_data()
    await message.answer(
        f"Поток: {data['flow']}\n"
        f"Язык: {data['language']}\n"
        f"Ключевые слова: {', '.join(data['keywords'])}\n"
        f"Модель: {model}",
        reply_markup=ReplyKeyboardRemove()
    )
    global listener
    listener = Listener(
        flow=data['flow'],
        keywords=data['keywords'],
        language=data['language'],
        analyzer_model=model,
        loop=asyncio.get_event_loop()
    )
    listener.start()

    await message.answer(
        "Анализ начался...",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Закончить анализ"),
                    KeyboardButton(text="Каналы"),
                ]
            ],
            resize_keyboard=True,
        )
    )

    await state.clear()


@router.message(F.text == "Закончить анализ")
async def end_trs(sender: types.Message):
    await sender.answer("Завершаю анализ...")

    global listener
    listener.stop()
    listener.join(timeout=10)
    listener = None

    await sender.answer(
        "Анализ завершен!",
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
