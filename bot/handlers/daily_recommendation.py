from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from datetime import date

from infra.container import Container
from adapters.telegram_adapters.renderers. \
    daily_recommendation_renderer import DailyRecommendationRenderer
from adapters.telegram_adapters.renderers.types import RenderMessage
from adapters.data_adapters.outfit_image_renderer import OutfitImageRenderer
from bot.helpers.load_tg_image import LoaderTgImage
from commands.daily_recommendation import DailyRecommendation, \
    DailyRecommendationResult

router = Router()


async def send_daily_to_user(bot: Bot, container: Container, user_id: int):
    daily_rec: DailyRecommendation = container.daily_recommendation()
    result: DailyRecommendationResult = await daily_rec.run(user_id=user_id,
                                                            today=date.today())

    renderer = DailyRecommendationRenderer()
    rendered: RenderMessage = renderer.render(result=result)

    if result.outfit is None:
        await bot.send_message(
            chat_id=user_id,
            text=rendered.text,
            reply_markup=rendered.keyboard,
            parse_mode="HTML",
        )
        return

    image_renderer = OutfitImageRenderer()
    loader = LoaderTgImage(bot=bot)

    image_bytes = await image_renderer.render_outfit(
        outfit=result.outfit,
        load_image=loader.load_tg_image,
    )

    await bot.send_photo(
        chat_id=user_id,
        photo=BufferedInputFile(image_bytes, filename="outfit.png"),
        caption=rendered.text,
        reply_markup=rendered.keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "daily:build")
async def daily_recommendation(cb: CallbackQuery, state: FSMContext,
                               container: Container):
    await state.clear()
    if cb.bot is None:
        await cb.answer()
        return
    await send_daily_to_user(cb.bot, container, cb.from_user.id)
    await cb.answer()
