from __future__ import annotations

from datetime import time, date
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from infra.container import Container
from adapters.telegram_adapters.renderers.types import RenderButton
from bot.keyboards import prefs_keyboards
from bot.keyboards.keyboard_helper import kb

from domain.models.user import User, ColdSensitivity
from domain.models.clothing_item import Style
from domain.models.weather_snap import WeatherSnap

from commands.manage_user_preferences import ManageUserPreferencesResult
from adapters.telegram_adapters.renderers.preferences_renderer import (
    ManageUserPreferencesRenderer,
)

router = Router()


class Prefs(StatesGroup):
    edit_gender = State()
    edit_age = State()
    edit_location = State()
    edit_notification_time = State()
    edit_cold = State()
    edit_style = State()
    edit_notifications = State()
    edit_season_notifications = State()


@router.callback_query(F.data == "prefs:open")
async def start(cb: CallbackQuery, state: FSMContext, container: Container):
    await state.clear()

    user_repo = container.user_repo()

    user: Optional[User] = user_repo.get(cb.from_user.id)

    if user is not None:
        renderer = ManageUserPreferencesRenderer()
        text = "🎛 НАСТРОЙКИ\n\n" + renderer.render_user_summary(user)
        if cb.message is not None:
            await cb.message.answer(text=text,
                                    reply_markup=prefs_keyboards.PrefsKeyboard)
            await cb.answer()
    else:
        if cb.message is not None:
            await cb.message.answer(
                "Не могу тебя найти, давай зарегистрируемся!\n\n"
                "Введи команду /start",
            )
            await cb.answer()


# GENDER
@router.callback_query(F.data == "prefs:edit:gender")
async def gender(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_gender)
    if cb.message is not None:
        await cb.message.answer(
                "Укажи свой пол:",
                reply_markup=kb([
                    [
                        RenderButton("👩 Женский", "prefs:edit:gender:female"),
                        RenderButton("👨 Мужской", "prefs:edit:gender:male"),
                    ]
                ])
            )
        await cb.answer()


@router.callback_query(Prefs.edit_gender,
                       F.data.startswith("prefs:edit:gender:"))
async def gender_edit(cb: CallbackQuery, state: FSMContext,
                      container: Container):
    if cb.data is not None and cb.message is not None:
        gender = cb.data.split(":")[-1]
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=cb.from_user.id,
                                              gender=gender)
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await cb.message.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )
        await cb.answer()


# AGE
@router.callback_query(F.data == "prefs:edit:age")
async def age(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_age)
    if cb.message is not None:
        await cb.message.answer("Сколько тебе лет?")
        await cb.answer()


@router.message(Prefs.edit_age)
async def age_edit(msg: Message, state: FSMContext, container: Container):
    if msg.text is not None and msg.from_user is not None:
        if not msg.text.isdigit():
            await msg.answer("Введите возраст числом 🙏")
            return
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=msg.from_user.id,
                                              age=int(msg.text))
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await msg.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )


# LOCATION
@router.callback_query(F.data == "prefs:edit:location")
async def location(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_location)
    if cb.message is not None:
        await cb.message.answer("В каком ты городе?\n"
                                "Напиши название на английском")
        await cb.answer()


@router.message(Prefs.edit_location)
async def location_edit(msg: Message, state: FSMContext, container: Container):
    usercase = container.weather_repo()
    if msg.text is not None and msg.from_user is not None:
        weather: Optional[WeatherSnap] = \
            usercase.get_weather(required_date=date.today(),
                                 city=msg.text.strip())
        if weather is None:
            await msg.answer("Неверный формат. Попробуй написать по-другому")
            return

        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=msg.from_user.id,
                                              location=msg.text.strip())
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await msg.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )


# TIME
@router.callback_query(F.data == "prefs:edit:time")
async def notif_time(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_notification_time)
    if cb.message is not None:
        await cb.message.answer("Во сколько ты хочешь получать уведомления?\n"
                                "Напиши в формате HH:MM")
        await cb.answer()


@router.message(Prefs.edit_notification_time)
async def notif_time_edit(msg: Message, state: FSMContext,
                          container: Container):
    if msg.text is not None and msg.from_user is not None:
        try:
            h, m = map(int, msg.text.split(":"))
            notif_time = time(hour=h, minute=m)
        except Exception:
            await msg.answer("Неверный формат 😔 Напиши HH:MM")
            return
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=msg.from_user.id,
                                              notification_time=notif_time)
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await msg.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )


# COLD SENSITIVITY
@router.callback_query(F.data == "prefs:edit:cold")
async def cold(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_cold)
    if cb.message is not None:
        await cb.message.answer(
            "Насколько ты мерзливый? 🥶",
            reply_markup=kb([
                    [RenderButton("❄️ Очень", "prefs:edit:cold:high")],
                    [RenderButton("🙂 50/50", "prefs:edit:cold:medium")],
                    [RenderButton("🔥 Вообще нет", "prefs:edit:cold:low")]
                ]
            )
        )
        await cb.answer()


@router.callback_query(Prefs.edit_cold,
                       F.data.startswith("prefs:edit:cold:"))
async def cold_edit(cb: CallbackQuery, state: FSMContext,
                    container: Container):
    if cb.data is not None and cb.message is not None:
        cold = cb.data.split(":")[-1]
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs. \
            update_preferences(user_id=cb.from_user.id,
                               cold_sensitivity=ColdSensitivity(cold))
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await cb.message.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )
        await cb.answer()


# STYLE
@router.callback_query(F.data == "prefs:edit:style")
async def style(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_style)
    if cb.message is not None:
        await cb.message.answer(
                "Какой стиль тебе ближе?",
                reply_markup=kb([
                    [
                        RenderButton("👕 Кэжуал", "prefs:edit:style:casual"),
                        RenderButton("🧥 Официальный",
                                     "prefs:edit:style:official"),
                    ],
                    [
                        RenderButton("🏃 Спортивный", "prefs:edit:style:sport"),
                        RenderButton("🎉 Вечерний", "prefs:edit:style:party"),
                    ],
                    [
                        RenderButton("🛹 Уличный", "prefs:edit:style:street"),
                        RenderButton("🌲 Aутдор", "prefs:edit:style:outdoor"),
                    ],
                ])
            )
        await cb.answer()


@router.callback_query(Prefs.edit_style,
                       F.data.startswith("prefs:edit:style:"))
async def style_edit(cb: CallbackQuery, state: FSMContext,
                     container: Container):
    if cb.data is not None and cb.message is not None:
        style = cb.data.split(":")[-1]
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=cb.from_user.id,
                                              favourite_style=Style(style))
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await cb.message.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )
        await cb.answer()


# DAILY NOTIFICATIONS
@router.callback_query(F.data == "prefs:edit:notif")
async def notifications(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_notifications)
    if cb.message is not None:
        await cb.message.answer(
                "Ежедневные уведомления",
                reply_markup=kb([
                    [
                        RenderButton("✅ Включить", "prefs:edit:notif:on"),
                        RenderButton("❌ Выключить", "prefs:edit:notif:off"),
                    ],
                ])
            )
        await cb.answer()


@router.callback_query(Prefs.edit_notifications,
                       F.data.startswith("prefs:edit:notif:"))
async def notifications_edit(cb: CallbackQuery, state: FSMContext,
                             container: Container):
    if cb.data is not None and cb.message is not None:
        enabled = cb.data.endswith("on")
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs.update_preferences(user_id=cb.from_user.id,
                                              notifications_enabled=enabled)
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await cb.message.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )
        await cb.answer()


# SEASON NOTIFICATIONS
@router.callback_query(F.data == "prefs:edit:season_notif")
async def season(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Prefs.edit_season_notifications)
    if cb.message is not None:
        await cb.message.answer(
                "Сезонные уведомления",
                reply_markup=kb([
                    [
                        RenderButton("✅ Включить",
                                     "prefs:edit:season_notif:on"),
                        RenderButton("❌ Выключить",
                                     "prefs:edit:season_notif:off"),
                    ],
                ])
            )
        await cb.answer()


@router.callback_query(Prefs.edit_season_notifications,
                       F.data.startswith("prefs:edit:season_notif:"))
async def season_edit(cb: CallbackQuery, state: FSMContext,
                      container: Container):
    if cb.data is not None and cb.message is not None:
        enabled = cb.data.endswith("on")
        await state.clear()
        manage_prefs = container.manage_user_preferences()
        result: ManageUserPreferencesResult \
            = manage_prefs. \
            update_preferences(user_id=cb.from_user.id,
                               season_notifications_enabled=enabled)
        renderer = ManageUserPreferencesRenderer()
        renderered = renderer.render(result=result)

        await cb.message.answer(
                text=renderered.text,
                reply_markup=renderered.keyboard
            )
        await cb.answer()
