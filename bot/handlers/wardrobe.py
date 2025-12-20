from aiogram import Router, F
from aiogram.types import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from domain.models.clothing_item import (ClothingCategory, ClothingItem,
                                         ClothingSubtype, Color, Style,
                                         WarmthLevel)
from commands.manage_wardrobe import ManageWardrobe
from adapters.telegram_adapters.renderers.wardrobe_renderer \
    import ManageWardrobeRenderer, _item_summary
from adapters.telegram_adapters.renderers.types import RenderButton
from infra.container import Container
from bot.keyboards.keyboard_helper import _kb, text_kb
from bot.keyboards import wardrobe_keyboards
from aiogram.types import ReplyKeyboardRemove


router = Router()


class ClothingItemSetup(StatesGroup):
    # базовое
    name = State()
    image_id = State()

    # классификация
    category = State()
    subtype = State()
    main_color = State()
    style = State()
    warmth_level = State()

    is_waterproof = State()
    is_windproof = State()

    # финал/подтверждение
    confirm = State()         # показать summary и кнопки "сохранить/отмена"


@router.callback_query(F.data.in_({"wardrobe:open", "wardrobe:add:cancel"}))
async def wardrobe_open(cb: CallbackQuery, state: FSMContext,
                        container: Container):
    await state.clear()

    user_repo = container.user_repo()

    user = user_repo.get(cb.from_user.id)

    if user is not None:
        await cb.message.answer(
            "Добро пожаловать в гардероб 🧥!\n"
            "Что будем делать?",
            reply_markup=_kb([
                [RenderButton("➕ Добавить вещь", "wardrobe:add")],
                [RenderButton("✏️ Изменить вещь", "wardrobe:update")],
                [RenderButton("🗑 Удалить вещь", "wardrobe:delete")],
                [
                    RenderButton("🏠 Меню", "menu:home"),
                    RenderButton("⚙️ Настройки", "prefs:open"),
                ],
            ])
        )
        await cb.answer()
        return

    await cb.message.answer(
        "Не могу тебя найти, давай зарегистрируемся!\n\n"
        "Введи команду /start",
    )
    await cb.answer()


@router.callback_query(F.data == "wardrobe:add")
async def wardrobe_add(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ClothingItemSetup.name)
    await state.update_data(mode="add")

    await cb.message.answer("Как назовём вещь? (например: «Белая рубашка»)")
    await cb.answer()


@router.callback_query(F.data == "wardrobe:update")
async def wardrobe_update(cb: CallbackQuery, state: FSMContext,
                          container: Container):
    await state.clear()
    await state.update_data(mode="update")

    await cb.message.answer(
        "Какую вещь хочешь изменить?",
        reply_markup=wardrobe_keyboards.UserItemsKeyboard(
            user_id=cb.from_user.id,
            wardrobe_repo=container.wardrobe_repo(),
            action="edit")
    )
    await cb.answer()


@router.callback_query(F.data.startswith("item:edit:"))
async def item_edit(cb: CallbackQuery, state: FSMContext,
                    container: Container):
    item_id = int(cb.data.split(":")[-1])

    repo = container.wardrobe_repo()
    item = repo.get_item(user_id=cb.from_user.id, item_id=item_id)

    if not item:
        await cb.answer("Вещь не найдена 😔", show_alert=True)
        return

    # сохраняем item_id + текущие данные
    await state.update_data(
        mode="update",
        item_id=item.item_id,
        name=item.name,
        image_id=item.image_id,
        category=item.category.value,
        subtype=item.subtype.value,
        main_color=item.main_color.value,
        style=item.style.value,
        warmth_level=item.warmth_level.value,
        is_waterproof=item.is_waterproof,
        is_windproof=item.is_windproof,
    )

    await state.set_state(ClothingItemSetup.name)

    await cb.message.answer(
        f"Редактируем: **{item.name}**\n"
        "Напиши новое название или нажми «Оставить как есть»",
        reply_markup=text_kb("Оставить как есть")
    )
    await cb.answer()


@router.message(ClothingItemSetup.name)
async def item_name(msg: Message, state: FSMContext):
    data = await state.get_data()

    if msg.text == "Оставить как есть" and data["mode"] == "update":
        pass
    else:
        name = (msg.text or "").strip()
        if not name:
            await msg.answer("Название пустое 😶. Напиши нормальное название.")
            return
        await state.update_data(name=name)

    await state.set_state(ClothingItemSetup.category)
    await msg.answer(
        "Ок, идем дальше",
        reply_markup=ReplyKeyboardRemove()
    )

    await msg.answer(
        "Выбери категорию:",
        reply_markup=_kb([[
            RenderButton("🧥 Верхняя одежда", "item:cat:outerwear"),
            RenderButton("👕 Верх", "item:cat:top"),
            RenderButton("👖 Низ", "item:cat:bottom"),
        ]])
    )


@router.callback_query(ClothingItemSetup.category,
                       F.data.startswith("item:cat:"))
async def item_category(cb: CallbackQuery, state: FSMContext):
    category = cb.data.split(':')[-1]
    await state.update_data(category=category)
    await state.set_state(ClothingItemSetup.subtype)
    if category == "outerwear":
        await cb.message.answer(
            "Выбери подкатегорию:",
            reply_markup=wardrobe_keyboards.OuterwearSubtypeKeyboard
        )
        await cb.answer()
    elif category == "top":
        await cb.message.answer(
            "Выбери подкатегорию:",
            reply_markup=wardrobe_keyboards.TopSubtypeKeyboard
        )
        await cb.answer()
    else:
        await cb.message.answer(
            "Выбери подкатегорию:",
            reply_markup=wardrobe_keyboards.BottomSubtypeKeyboard
        )
        await cb.answer()


@router.callback_query(ClothingItemSetup.subtype,
                       F.data.startswith("item:subtype:"))
async def item_subtype(cb: CallbackQuery, state: FSMContext):
    subtype = cb.data.split(':')[-1]
    await state.update_data(subtype=subtype)
    await state.set_state(ClothingItemSetup.main_color)
    await cb.message.answer(
            "Выбери цвет:",
            reply_markup=wardrobe_keyboards.ColorKeyboard
        )
    await cb.answer()


@router.callback_query(ClothingItemSetup.main_color,
                       F.data.startswith("item:color:"))
async def item_color(cb: CallbackQuery, state: FSMContext):
    main_color = cb.data.split(':')[-1]
    await state.update_data(main_color=main_color)
    await state.set_state(ClothingItemSetup.style)
    await cb.message.answer(
            "Выбери стиль:",
            reply_markup=wardrobe_keyboards.StyleKeyboard
        )
    await cb.answer()


@router.callback_query(ClothingItemSetup.style,
                       F.data.startswith("item:style:"))
async def item_style(cb: CallbackQuery, state: FSMContext):
    style = cb.data.split(':')[-1]
    await state.update_data(style=style)
    await state.set_state(ClothingItemSetup.warmth_level)
    await cb.message.answer(
            "Выбери насколько вещь теплая:",
            reply_markup=wardrobe_keyboards.WarmthKeyboard
        )
    await cb.answer()


async def ask_image_in_edit(cb: CallbackQuery, state: FSMContext,
                            image_id: str):

    await state.set_state(ClothingItemSetup.image_id)
    await state.update_data(
        mode="edit",
        image_id=image_id,
        awaiting_new_image=False,
    )

    # покажем текущее фото
    await cb.message.answer_photo(
        photo=image_id,
        caption="Текущее фото. Хочешь заменить?",
        reply_markup=_kb([[
            RenderButton("✅ Да, заменить", "item:image:change"),
            RenderButton("👌 Оставить как есть", "item:image:keep"),
        ]])
    )
    await cb.answer()


async def ask_image_in_add(msg: Message, state: FSMContext):
    await state.set_state(ClothingItemSetup.image_id)
    await state.update_data(mode="add")
    await msg.answer("Теперь отправь фото вещи (или файл).")


@router.callback_query(ClothingItemSetup.warmth_level,
                       F.data.startswith("item:warmth:"))
async def item_warmth(cb: CallbackQuery, state: FSMContext):
    warmth = cb.data.split(':')[-1]
    await state.update_data(warmth_level=warmth)
    data = await state.get_data()
    if data["category"] == "outerwear":
        await state.set_state(ClothingItemSetup.is_waterproof)
        await cb.message.answer(
                "Вещь водонепроницаемая?",
                reply_markup=wardrobe_keyboards.YesNoKeyboard
            )
        await cb.answer()
    else:
        await state.set_state(ClothingItemSetup.image_id)
        await state.update_data(is_waterproof=False, is_windproof=False)
        data = await state.get_data()
        mode = data.get("mode", "add")
        if mode == "add":
            await ask_image_in_add(cb.message, state)
        else:
            await ask_image_in_edit(
                cb,
                state,
                image_id=data["image_id"]
            )


@router.callback_query(ClothingItemSetup.is_waterproof,
                       F.data.in_({"item:yes", "item:no"}))
async def item_waterproof(cb: CallbackQuery, state: FSMContext):
    is_waterproof = cb.data.split(':')[-1] == "yes"
    await state.update_data(is_waterproof=is_waterproof)
    data = await state.get_data()
    await state.set_state(ClothingItemSetup.is_windproof)
    if data["category"] == "outerwear":
        await cb.message.answer(
                "Вещь ветрозащитная?",
                reply_markup=wardrobe_keyboards.YesNoKeyboard
            )
        await cb.answer()


@router.callback_query(ClothingItemSetup.is_windproof,
                       F.data.in_({"item:yes", "item:no"}))
async def item_windproof(cb: CallbackQuery, state: FSMContext):
    is_windproof = cb.data.split(':')[-1] == "yes"
    await state.update_data(is_windproof=is_windproof)
    await state.set_state(ClothingItemSetup.image_id)
    data = await state.get_data()
    mode = data.get("mode", "add")
    if mode == "add":
        await ask_image_in_add(cb.message, state)
    else:
        await ask_image_in_edit(
            cb,
            state,
            image_id=data["image_id"]
        )


@router.message(
    ClothingItemSetup.image_id,
    F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT})
)
async def item_photo(msg: Message, state: FSMContext):
    """
    Принимает фото/файл.
    В add — всегда принимает.
    В edit — принимает только если ранее нажали 'заменить'
    (awaiting_new_image=True).
    """
    data = await state.get_data()
    mode = data.get("mode", "add")

    if mode == "edit" and not data.get("awaiting_new_image"):
        await msg.answer("Сначала нажми «Да, заменить»"
                         "или «Оставить как есть».")
        return

    image_id = None
    if msg.photo:
        image_id = msg.photo[-1].file_id
    elif msg.document:
        image_id = msg.document.file_id

    if not image_id:
        await msg.answer("Не вижу фото/файл 😶 Попробуй ещё раз.")
        return

    await state.update_data(image_id=image_id, awaiting_new_image=False)
    await state.set_state(ClothingItemSetup.confirm)

    data = await state.get_data()
    confirm_cb = "wardrobe:add:confirm" if mode == "add" \
        else "wardrobe:edit:confirm"

    await msg.answer(
        _item_summary(data),
        reply_markup=_kb([[
            RenderButton("✅ Сохранить", confirm_cb),
            RenderButton("❌ Отмена", "wardrobe:add:cancel"),
        ]])
    )


@router.callback_query(ClothingItemSetup.image_id,
                       F.data == "item:image:change")
async def item_image_change(cb: CallbackQuery, state: FSMContext):
    """
    Пользователь решил заменить фото.
    """
    await state.update_data(awaiting_new_image=True)
    await cb.message.answer("Ок, пришли новое фото (или файл).")
    await cb.answer()


@router.callback_query(ClothingItemSetup.image_id, F.data == "item:image:keep")
async def item_image_keep(cb: CallbackQuery, state: FSMContext):
    """
    Пользователь оставляет старое фото.
    Переходим сразу в confirm.
    """
    data = await state.get_data()
    image_id = data.get("image_id")

    if not image_id:
        # на всякий случай
        await cb.message.answer("Не вижу текущую картинку 😶."
                                "Пришли фото заново.")
        await cb.answer()
        return

    await state.update_data(image_id=image_id,
                            awaiting_new_image=False)
    await state.set_state(ClothingItemSetup.confirm)

    data = await state.get_data()
    confirm_cb = "wardrobe:add:confirm" if data.get("mode", "add") == "add" \
        else "wardrobe:edit:confirm"

    await cb.message.answer(
        _item_summary(data),
        reply_markup=_kb([[
            RenderButton("✅ Сохранить", confirm_cb),
            RenderButton("❌ Отмена", "wardrobe:add:cancel"),
        ]])
    )
    await cb.answer()


@router.callback_query(
    ClothingItemSetup.confirm,
    F.data.in_({"wardrobe:add:confirm", "wardrobe:edit:confirm"}))
async def item_confirm(cb: CallbackQuery, state: FSMContext,
                       container: Container):
    data = await state.get_data()
    user_id = cb.from_user.id

    usecase: ManageWardrobe = container.manage_wardrobe()
    renderer = ManageWardrobeRenderer()

    mode = data.get("mode", "add")
    item = ClothingItem(
            item_id=int(data.get("item_id", 0)),
            owner_id=user_id,
            image_id=str(data["image_id"]),
            name=str(data["name"]),
            category=ClothingCategory(data["category"]),
            main_color=Color(data["main_color"]),
            style=Style(data["style"]),
            warmth_level=WarmthLevel(data["warmth_level"]),
            subtype=ClothingSubtype(data["subtype"]),
            is_waterproof=bool(data.get("is_waterproof")),
            is_windproof=bool(data.get("is_windproof")),
        )
    if mode == "add":
        result = usecase.add_item(user_id=user_id, item=item)
    else:
        result = usecase.update_item(user_id=user_id, item_id=item.item_id, **{
            "name": item.name,
            "image_id": item.image_id,
            "category": item.category,
            "subtype": item.subtype,
            "main_color": item.main_color,
            "style": item.style,
            "warmth_level": item.warmth_level,
            "is_waterproof": item.is_waterproof,
            "is_windproof": item.is_windproof,
        })
    rendered = renderer.render(result)

    await state.clear()
    await cb.message.answer(
        rendered.text,
        reply_markup=rendered.keyboard
    )
    await cb.answer()


@router.callback_query(F.data == "wardrobe:delete")
async def delete(cb: CallbackQuery, container: Container):
    await cb.message.answer(
        "Какую вещь хочешь удалить?",
        reply_markup=wardrobe_keyboards.UserItemsKeyboard(
            user_id=cb.from_user.id,
            wardrobe_repo=container.wardrobe_repo(), action="delete")
    )
    await cb.answer()


@router.callback_query(F.data.startswith("item:delete:"))
async def delete_item(cb: CallbackQuery, container: Container):
    item_id = int(cb.data.split(":")[-1])
    user_id = cb.from_user.id

    usecase: ManageWardrobe = container.manage_wardrobe()
    renderer = ManageWardrobeRenderer()

    result = usecase.delete_item(
        user_id=user_id,
        item_id=item_id,
    )

    rendered = renderer.render(result)

    await cb.message.answer(
        rendered.text,
        reply_markup=rendered.keyboard
    )
    await cb.answer()
