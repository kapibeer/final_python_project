from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from infra.container import Container

from bot.keyboards import outfit_keyboards
from bot.helpers.load_tg_image import LoaderTgImage

from adapters.telegram_adapters.renderers.build_outfit_renderer \
    import OutfitBuildRenderer, renderer_like
from adapters.data_adapters.outfit_image_renderer import OutfitImageRenderer

from domain.models.user import User
from domain.models.clothing_item import Style
from domain.models.weather_snap import WeatherSnap
from domain.models.outfit import Outfit

from commands.build_outfit import BuildOutfitResult

router = Router()


class OutfitBuild(StatesGroup):
    outfit_location = State()
    outfit_date = State()
    outfit_style = State()


def _build_intro_text() -> str:
    return (
        "<b>Давай подберем тебе аутфит!</b> ✨\n\n"
        "Если хочешь поменять дату, стиль или город — нажми кнопку ниже 🌸\n\n"
        "<blockquote>учти: мы не можем спрогнозировать"
        " погоду дальше чем на две недели!</blockquote>"
    )


@router.callback_query(F.data == "outfit:build")
async def outfit_build(cb: CallbackQuery, state: FSMContext,
                       container: Container):
    await state.clear()

    user_repo = container.user_repo()
    user: Optional[User] = user_repo.get(cb.from_user.id)

    if user is None:
        if cb.message is not None:
            await cb.message.answer(
                "Не могу тебя найти 😶\n"
                "Введи команду /start",
            )
        await cb.answer()
        return

    await state.update_data(
        outfit_location=user.location,
        outfit_style=user.favourite_style.value,
        outfit_date=date.today().isoformat(),
    )

    if cb.message is not None:
        await cb.message.answer(
            text=_build_intro_text(),
            reply_markup=outfit_keyboards.EditKeyboard,
            parse_mode="HTML"
        )
    await cb.answer()


# LOCATION
@router.callback_query(F.data == "outfit:edit:location")
async def outfit_edit_location(cb: CallbackQuery, state: FSMContext):
    await state.set_state(OutfitBuild.outfit_location)
    if cb.message is not None:
        await cb.message.answer("Напиши город (на английском)")
    await cb.answer()


@router.message(OutfitBuild.outfit_location)
async def outfit_location_msg(msg: Message, state: FSMContext,
                              container: Container):
    city = (msg.text or "").strip()
    if not city:
        await msg.answer("Город пустой 😶. Напиши нормальное название.")
        return

    weather_repo = container.weather_repo()
    weather: Optional[WeatherSnap] = \
        weather_repo.get_weather(required_date=date.today(), city=city)
    if weather is None:
        await msg.answer("Не смог найти этот город 😔.\n"
                         "Попробуй написать иначе.")
        return

    await state.update_data(outfit_location=city)
    await state.set_state(None)
    await msg.answer("✅ Город обновлён!",
                     reply_markup=outfit_keyboards.EditKeyboard)


# STYLE
@router.callback_query(F.data == "outfit:edit:style")
async def outfit_edit_style(cb: CallbackQuery, state: FSMContext):
    await state.set_state(OutfitBuild.outfit_style)
    if cb.message is not None:
        await cb.message.answer(
            "Выбери стиль:",
            reply_markup=outfit_keyboards.StyleKeyboard
        )
    await cb.answer()


@router.callback_query(OutfitBuild.outfit_style,
                       F.data.startswith("outfit:style:"))
async def outfit_style_cb(cb: CallbackQuery, state: FSMContext):
    if cb.data is None:
        await cb.answer()
        return

    style_value = cb.data.split(":")[-1]
    await state.update_data(outfit_style=style_value)
    await state.set_state(None)
    if cb.message is not None:
        await cb.message.answer("✅ Стиль обновлён!",
                                reply_markup=outfit_keyboards.EditKeyboard)
    await cb.answer()


# DATE
@router.callback_query(F.data == "outfit:edit:date")
async def outfit_edit_date(cb: CallbackQuery, state: FSMContext):
    await state.set_state(OutfitBuild.outfit_date)
    if cb.message is not None:
        await cb.message.answer(
            "Выбери дату:\n"
            "• Напиши в формате YYYY-MM-DD (например 2025-12-21)\n"
            "• или нажми быстрые кнопки:",
            reply_markup=outfit_keyboards.DateQuickKeyboard
        )
    await cb.answer()


@router.callback_query(OutfitBuild.outfit_date,
                       F.data.startswith("outfit:date:"))
async def outfit_date_quick(cb: CallbackQuery, state: FSMContext):
    if cb.data is None:
        await cb.answer()
        return

    kind = cb.data.split(":")[-1]
    d = date.today()
    if kind == "today":
        target = d
    elif kind == "tomorrow":
        target = d + timedelta(days=1)
    else:
        target = d  # fallback

    await state.update_data(outfit_date=target.isoformat())
    await state.set_state(None)
    if cb.message is not None:
        await cb.message.answer("✅ Дата обновлена!",
                                reply_markup=outfit_keyboards.EditKeyboard)
    await cb.answer()


@router.message(OutfitBuild.outfit_date)
async def outfit_date_msg(msg: Message, state: FSMContext,
                          container: Container):
    raw = (msg.text or "").strip()
    try:
        target = date.fromisoformat(raw)
    except Exception:
        await msg.answer("Неверный формат 😔"
                         " Напиши YYYY-MM-DD, например 2025-12-21",
                         reply_markup=outfit_keyboards.DateQuickKeyboard)
        return

    # проверка на диапазон
    today = date.today()
    if target < today or target > today + timedelta(days=13):
        await msg.answer("Я могу смотреть погоду только на 14 дней вперёд 😔",
                         reply_markup=outfit_keyboards.DateQuickKeyboard)
        return

    data = await state.get_data()
    city = str(data.get("outfit_location") or "").strip()
    if city:
        weather_repo = container.weather_repo()
        weather = weather_repo.get_weather(required_date=target, city=city)
        if weather is None:
            await msg.answer("Не смог найти погоду на эту дату/город 😔"
                             " Попробуй другое.")
            return

    await state.update_data(outfit_date=target.isoformat())
    await state.set_state(None)
    await msg.answer("✅ Дата обновлена!",
                     reply_markup=outfit_keyboards.EditKeyboard,)


# GEN
@router.callback_query(F.data == "outfit:gen")
async def outfit_gen(cb: CallbackQuery, state: FSMContext,
                     container: Container):
    data = await state.get_data()

    city = str(data.get("outfit_location") or "").strip()
    style_raw = str(data.get("outfit_style") or "").strip()
    date_raw = str(data.get("outfit_date") or "").strip()

    if not city or not date_raw:
        user = container.user_repo().get(cb.from_user.id)
        if user is None:
            if cb.message is not None:
                await cb.message.answer("Не нашёл профиль 😶 /start")
            await cb.answer()
            return
        city = city or user.location
        date_raw = date_raw or date.today().isoformat()
        style_raw = style_raw or user.favourite_style.value

    # валидируем дату + стиль
    try:
        target_date = date.fromisoformat(date_raw)
    except Exception:
        target_date = date.today()

    style: Optional[Style]
    try:
        style = Style(style_raw) if style_raw else None
    except Exception:
        style = Style.CASUAL
    await state.update_data(target_style=style)
    weather_repo = container.weather_repo()
    weather: Optional[WeatherSnap] = \
        weather_repo.get_weather(required_date=target_date, city=city)
    if weather is None:
        if cb.message is not None:
            await cb.message.answer("Не смог получить погоду 😔"
                                    " Попробуй поменять город/датy.",
                                    reply_markup=outfit_keyboards.EditKeyboard)
        await cb.answer()
        return

    build_outfit = container.build_outfit()

    result: BuildOutfitResult = build_outfit.run(user_id=cb.from_user.id,
                                                 today=target_date, city=city,
                                                 style=style, count_max=5)
    await state.update_data(outfit_result=result)
    renderer = OutfitBuildRenderer()
    rendered = renderer.render(result=result, index=0)
    if result.outfits is not None:
        outfit: Outfit = result.outfits[0]
        image_renderer = OutfitImageRenderer()
        loader = LoaderTgImage(bot=cb.bot)
        image_rendered = await \
            image_renderer.render_outfit(outfit=outfit,
                                         load_image=loader.load_tg_image)
        if cb.message is not None:
            await cb.message.answer_photo(
                photo=BufferedInputFile(image_rendered, filename="outfit.png"),
                caption=rendered.text,
                reply_markup=rendered.keyboard,
                parse_mode="HTML"
            )
            await cb.answer()
            return
    if cb.message is not None:
        await cb.message.answer(text=rendered.text,
                                reply_markup=rendered.keyboard,
                                parse_mode="HTML")
    await cb.answer()


# NEXT
@router.callback_query(F.data.startswith("outfit:next:"))
async def outfit_next(cb: CallbackQuery, state: FSMContext,
                      container: Container) -> None:
    indx = 0
    if cb.data is not None:
        indx = int(cb.data.split(':')[-1])
    data = await state.get_data()
    result: BuildOutfitResult = data.get("outfit_result") \
        or BuildOutfitResult(success=False, message_key="")
    renderer = OutfitBuildRenderer()
    rendered = renderer.render(result=result, index=indx)
    if result.outfits is not None:
        outfit: Outfit = result.outfits[indx]
        image_renderer = OutfitImageRenderer()
        loader = LoaderTgImage(bot=cb.bot)
        image_rendered = await \
            image_renderer.render_outfit(outfit=outfit,
                                         load_image=loader.load_tg_image)
        if cb.message is not None:
            await cb.message.answer_photo(
                photo=BufferedInputFile(image_rendered, filename="outfit.png"),
                caption=rendered.text,
                reply_markup=rendered.keyboard,
                parse_mode="HTML"
            )
            await cb.answer()
            return
    if cb.message is not None:
        await cb.message.answer(text=rendered.text,
                                reply_markup=rendered.keyboard,
                                parse_mode="HTML")
    await cb.answer()


# LIKE
@router.callback_query(F.data == "outfit:like")
async def menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    data = await state.get_data()
    style: Style = data.get("target_style") or Style.CASUAL
    if cb.message is not None:
        await cb.message.answer(
                    renderer_like(style=style),
                    reply_markup=outfit_keyboards.LikeKeyboard,
                    parse_mode="HTML")
    await cb.answer()
