from datetime import time, date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from domain.models.user import ColdSensitivity, User
from domain.models.weather_snap import WeatherSnap
from domain.models.clothing_item import Style
from adapters.telegram_adapters.renderers.types import RenderButton
from infra.container import Container
from bot.keyboards.keyboard_helper import _kb


router = Router()


class PrefsSetup(StatesGroup):
    gender = State()
    age = State()
    location = State()
    cold = State()
    style = State()
    notifications = State()
    season_notifications = State()
    notification_time = State()


@router.message(F.text == "/start")
async def start(msg: Message, state: FSMContext, container: Container):
    await state.clear()

    user_repo = container.user_repo()

    user = user_repo.get(msg.from_user.id)

    if user is not None:
        await msg.answer(
            f"С возвращением, {user.username or 'друг'} 👋\n"
            "Что будем делать?",
            reply_markup=_kb([
                [RenderButton("✨ Подобрать лук", "outfit:build")],
                [
                    RenderButton("🧥 Гардероб", "wardrobe:open"),
                    RenderButton("⚙️ Настройки", "prefs:open"),
                ],
            ])
        )
        return

    await state.set_state(PrefsSetup.gender)

    await msg.answer(
        "Привет! 👋\n"
        "Давай немного познакомимся.\n\n"
        "Укажи свой пол:",
        reply_markup=_kb([
            [
                RenderButton("👩 Женский", "prefs:gender:female"),
                RenderButton("👨 Мужской", "prefs:gender:male"),
            ]
        ])
    )


# GENDER
@router.callback_query(PrefsSetup.gender, F.data.startswith("prefs:gender:"))
async def gender(cb: CallbackQuery, state: FSMContext):
    gender = cb.data.split(":")[-1]
    await state.update_data(gender=gender)

    await state.set_state(PrefsSetup.age)
    await cb.message.answer("Сколько тебе лет?")
    await cb.answer()


# AGE
@router.message(PrefsSetup.age)
async def age(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Введите возраст числом 🙏")
        return

    await state.update_data(age=int(msg.text))
    await state.set_state(PrefsSetup.location)
    await msg.answer("В каком ты городе? Напиши название на английском")


# LOCATION
@router.message(PrefsSetup.location)
async def location(msg: Message, state: FSMContext, container: Container):
    usercase = container.weather_repo()
    weather: WeatherSnap = usercase.get_weather(required_date=date.today(),
                                                city=msg.text.strip())
    if weather is None:
        await msg.answer("Неверный формат. Попробуй написать по-другому")
        return
    await state.update_data(location=msg.text.strip())
    await state.set_state(PrefsSetup.cold)
    await msg.answer(
        "Ты мерзливый? 🥶",
        reply_markup=_kb([
            [[RenderButton("❄️ Да", "prefs:cold:high")],
             [RenderButton("🙂 50/50", "prefs:cold:medium")],
             [RenderButton("🔥 Нет, мне всегда жарко", "prefs:cold:low")]
             ]
        ])
    )


# COLD SENSITIVITY
@router.callback_query(PrefsSetup.cold, F.data.startswith("prefs:cold:"))
async def cold(cb: CallbackQuery, state: FSMContext):
    cold = cb.data.split(":")[-1]
    await state.update_data(cold_sensitivity=cold)

    await state.set_state(PrefsSetup.style)

    await cb.message.answer(
        "Какой стиль тебе ближе?",
        reply_markup=_kb([
            [
                RenderButton("👕 Кэжуал", "prefs:style:casual"),
                RenderButton("🧥 Официальный", "prefs:style:official"),
            ],
            [
                RenderButton("🏃 Спортивный", "prefs:style:sport"),
                RenderButton("🎉 Вечерний", "prefs:style:party"),
            ],
            [
                RenderButton("🛹 Уличный", "prefs:style:street"),
                RenderButton("🌲 Aутдор", "prefs:style:outdoor"),
            ],
        ])
    )
    await cb.answer()


# STYLE
@router.callback_query(PrefsSetup.style, F.data.startswith("prefs:style:"))
async def style(cb: CallbackQuery, state: FSMContext):
    style = cb.data.split(":")[-1]
    await state.update_data(favourite_style=style)

    await state.set_state(PrefsSetup.notifications)

    await cb.message.answer(
        "Хочешь получать ежедневные рекомендации?",
        reply_markup=_kb([
            [
                RenderButton("✅ Да", "prefs:notif:on"),
                RenderButton("❌ Нет", "prefs:notif:off"),
            ]
        ])
    )
    await cb.answer()


# DAILY NOTIFICATIONS
@router.callback_query(PrefsSetup.notifications,
                       F.data.startswith("prefs:notif:"))
async def notifications(cb: CallbackQuery, state: FSMContext):
    enabled = cb.data.endswith("on")
    await state.update_data(notifications_enabled=enabled)

    await state.set_state(PrefsSetup.season_notifications)

    await cb.message.answer(
        "Хочешь получать сезонные уведомления?",
        reply_markup=_kb([
            [
                RenderButton("✅ Да", "prefs:season:on"),
                RenderButton("🚫 Нет", "prefs:season:off"),
            ]
        ])
    )
    await cb.answer()


# SEASON NOTIFICATIONS
@router.callback_query(PrefsSetup.season_notifications,
                       F.data.startswith("prefs:season:"))
async def season(cb: CallbackQuery, state: FSMContext):
    enabled = cb.data.endswith("on")
    await state.update_data(season_notifications_enabled=enabled)

    await state.set_state(PrefsSetup.notification_time)
    await cb.message.answer(
        "Во сколько присылать уведомления?\n"
        "Напиши в формате: HH:MM (например 09:30)"
    )
    await cb.answer()


# TIME + SAVE
@router.message(PrefsSetup.notification_time)
async def notification_time_handler(msg: Message,
                                    state: FSMContext,
                                    container: Container):
    try:
        h, m = map(int, msg.text.split(":"))
        notif_time = time(hour=h, minute=m)
    except Exception:
        await msg.answer("Неверный формат 😔 Напиши HH:MM")
        return

    data = await state.get_data()

    repo = container.user_repo()

    existing = repo.get(msg.from_user.id)
    if existing is None:
        repo.create(User(
            user_id=msg.from_user.id,
            username=msg.from_user.username or "",
            gender=data["gender"],
            age=data["age"],
            location=data["location"],
            cold_sensitivity=ColdSensitivity(data["cold_sensitivity"]),
            favourite_style=Style(data["favourite_style"]),
            notifications_enabled=data["notifications_enabled"],
            season_notifications_enabled=data["season_notifications_enabled"],
            notification_time=notif_time,
        ))
    else:
        existing.username = msg.from_user.username or existing.username
        existing.gender = data["gender"]
        existing.age = data["age"]
        existing.location = data["location"]
        existing.cold_sensitivity = ColdSensitivity(data["cold_sensitivity"])
        existing.favourite_style = Style(data["favourite_style"])
        existing.notifications_enabled = data["notifications_enabled"]
        existing.season_notifications_enabled = \
            data["season_notifications_enabled"]
        existing.notification_time = notif_time
        repo.update(existing)

    await state.clear()

    await msg.answer(
        "Готово! 🎉\n"
        "Я всё запомнил ❤️",
        reply_markup=_kb([
            [RenderButton("✨ Подобрать лук", "outfit:build")],
            [
                RenderButton("🧥 Гардероб", "wardrobe:open"),
                RenderButton("🏠 Меню", "menu:home"),
            ],
        ])
    )
