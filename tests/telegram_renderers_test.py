# type: ignore
from datetime import date, time

from commands.build_outfit import BuildOutfitResult
from commands.weather_summary import WeatherSummary

from adapters.telegram_adapters.renderers.build_outfit_renderer import \
    OutfitBuildRenderer

from commands.daily_recommendation import DailyRecommendationResult
from domain.models.take_with import TakeWith

from adapters.telegram_adapters.renderers.daily_recommendation_renderer \
    import DailyRecommendationRenderer

from commands.manage_user_preferences import ManageUserPreferencesResult
from domain.models.user import ColdSensitivity
from adapters.telegram_adapters.renderers.preferences_renderer import (
    ManageUserPreferencesRenderer,
)

from commands.manage_wardrobe import ManageWardrobeResult
from adapters.telegram_adapters.renderers.wardrobe_renderer import (
    ManageWardrobeRenderer,
)

from domain.models.clothing_item import Style, ClothingCategory, \
    ClothingSubtype, WarmthLevel
from domain.models.outfit import Outfit

from tests.helpers import make_user, make_item


def test_render_not_found_error() -> None:
    r = OutfitBuildRenderer()

    result = BuildOutfitResult(
        success=False,
        message_key="not_found",
        outfits=None,
        weather=None,
        style_used=None,
    )

    msg = r.render(result=result, index=0)

    assert "не нашёл" in msg.text.lower()
    assert len(msg.buttons) == 1
    assert msg.buttons[0][0].text == "✅ Начать"
    assert msg.buttons[0][0].callback_data == "user:start"


def test_render_success_but_no_outfits_returns_empty_message() -> None:
    r = OutfitBuildRenderer()

    result = BuildOutfitResult(
        success=True,
        message_key="success",
        outfits=[],
        weather=WeatherSummary(
            city="Amsterdam",
            required_date=date(2025, 12, 24),
            temp_morning=1,
            temp_day=5,
            temp_evening=2,
            is_rain=False,
            is_snow=False,
            is_windy=False,
            coldness_level=3,
        ),
        style_used=None,
    )

    msg = r.render(result=result, index=0)

    assert "не смог собрать лук" in msg.text.lower()

    callbacks = [b.callback_data
                 for row in msg.buttons for b in row]
    assert "outfit:gen" in callbacks
    assert "outfit:like" in callbacks
    assert "wardrobe:add" in callbacks
    assert "menu:home" in callbacks


def test_outfit_renderer_empty_wardrobe_error() -> None:
    r = OutfitBuildRenderer()

    result = BuildOutfitResult(
        success=False,
        message_key="empty_wardrobe",
        outfits=None,
        weather=None,
        style_used=None,
    )

    msg = r.render(result=result, index=0)

    assert "пока нет вещей" in msg.text.lower()
    callbacks = [b.callback_data for row in msg.buttons for b in row]
    assert callbacks == ["menu:home", "wardrobe:add"]


def test_outfit_renderer_last_outfit_keyboard_has_gen_and_empty_row() -> None:
    r = OutfitBuildRenderer()

    outfit = Outfit(items=[
        make_item(item_id=1,
                  category=ClothingCategory.TOP,
                  subtype=ClothingSubtype.TSHIRT),
        make_item(item_id=2,
                  category=ClothingCategory.BOTTOM,
                  subtype=ClothingSubtype.JEANS),
    ])

    result = BuildOutfitResult(
        success=True,
        message_key="success",
        outfits=[outfit],
        weather=WeatherSummary(
            city="Amsterdam",
            required_date=date(2025, 12, 24),
            temp_morning=1,
            temp_day=5,
            temp_evening=2,
            is_rain=False,
            is_snow=False,
            is_windy=True,
            coldness_level=3,
        ),
        style_used=Style.CASUAL,
    )

    msg = r.render(result=result, index=0)

    assert len(msg.buttons) == 3
    assert msg.buttons[-1] == []

    callbacks = [b.callback_data for row in msg.buttons for b in row]
    assert "outfit:gen" in callbacks
    assert "wardrobe:open" in callbacks
    assert "menu:home" in callbacks


def test_outfit_renderer_index_is_clamped_to_last() -> None:
    r = OutfitBuildRenderer()

    outfit1 = Outfit(items=[make_item(item_id=1,
                                      category=ClothingCategory.TOP,
                                      subtype=ClothingSubtype.TSHIRT)])
    outfit2 = Outfit(items=[make_item(item_id=2, category=ClothingCategory.TOP,
                                      subtype=ClothingSubtype.SHIRT)])

    result = BuildOutfitResult(
        success=True,
        message_key="success",
        outfits=[outfit1, outfit2],
        weather=None,
        style_used=Style.CASUAL,
    )

    msg = r.render(result=result, index=999)

    assert "shirt" in msg.text.lower() or "рубаш" \
        in msg.text.lower() or "• <b>x</b>" in msg.text.lower()


def test_daily_renderer_not_found() -> None:
    r = DailyRecommendationRenderer()

    result = DailyRecommendationResult(
        success=False,
        message_key="not_found",
        outfit=None,
        weather=None,
        style_used=None,
        take_with=None,
    )

    msg = r.render(result)

    assert "не нашёл твой профиль" in msg.text.lower()
    assert msg.buttons[0][0].text == "✅ Начать"
    assert msg.buttons[0][0].callback_data == "user:start"


def test_daily_renderer_success_without_outfit_shows_add_item_buttons() \
        -> None:
    r = DailyRecommendationRenderer()

    result = DailyRecommendationResult(
        success=True,
        message_key="success",
        outfit=None,
        weather=WeatherSummary(
            city="Amsterdam",
            required_date=date(2025, 12, 24),
            temp_morning=1,
            temp_day=6,
            temp_evening=2,
            is_rain=True,
            is_snow=False,
            is_windy=False,
            coldness_level=3,
        ),
        style_used=Style.CASUAL,
        take_with=TakeWith(items=["зонт"]),
    )

    msg = r.render(result)

    assert "ежедневная" not in msg.text.lower()
    assert "не смог собрать лук" in msg.text.lower()
    assert "зонт" in msg.text.lower()

    callbacks = [b.callback_data
                 for row in msg.buttons for b in row]
    assert callbacks == ["menu:home", "wardrobe:add"]


def test_daily_renderer_success_without_take_with_does_not_show_block():
    r = DailyRecommendationRenderer()

    result = DailyRecommendationResult(
        success=True,
        message_key="success",
        outfit=None,
        weather=WeatherSummary(
            city="Amsterdam",
            required_date=date(2025, 12, 24),
            temp_morning=1,
            temp_day=6,
            temp_evening=2,
            is_rain=False,
            is_snow=True,
            is_windy=False,
            coldness_level=3,
        ),
        style_used=Style.CASUAL,
        take_with=None,
    )

    msg = r.render(result)

    assert "что взять с собой" not in msg.text.lower()
    assert "не смог собрать лук" in msg.text.lower()


def test_daily_renderer_header_contains_icons_when_weather_present() -> None:
    r = DailyRecommendationRenderer()

    result = DailyRecommendationResult(
        success=True,
        message_key="success",
        outfit=None,
        weather=WeatherSummary(
            city="Amsterdam",
            required_date=date(2025, 12, 24),
            temp_morning=1,
            temp_day=6,
            temp_evening=2,
            is_rain=True,
            is_snow=True,
            is_windy=True,
            coldness_level=3,
        ),
        style_used=Style.CASUAL,
        take_with=TakeWith(items=["зонт"]),
    )

    msg = r.render(result)

    assert "🌧" in msg.text
    assert "❄️" in msg.text
    assert "💨" in msg.text
    assert "amsterdam".lower() in msg.text.lower()


def test_manage_user_prefs_renderer_not_found() -> None:
    r = ManageUserPreferencesRenderer()

    result = ManageUserPreferencesResult(
        success=False,
        message_key="not_found",
        user=None,
    )

    msg = r.render(result)

    assert "не нашёл твой профиль" in msg.text.lower()
    assert msg.buttons[0][0].text == "✅ Начать"
    assert msg.buttons[0][0].callback_data == "user:start"


def test_manage_user_prefs_renderer_updated() -> None:
    r = ManageUserPreferencesRenderer()

    user = make_user(cs=ColdSensitivity.MEDIUM)
    user.favourite_style = Style.CASUAL

    result = ManageUserPreferencesResult(
        success=True,
        message_key="updated",
        user=user,
    )

    msg = r.render(result)

    assert "настройки обновлены" in msg.text.lower()

    callbacks = [b.callback_data
                 for row in msg.buttons for b in row]
    assert callbacks == ["prefs:open", "menu:home"]


def test_manage_user_prefs_renderer_user_summary_contains_all_fields() -> None:
    r = ManageUserPreferencesRenderer()

    user = make_user(cs=ColdSensitivity.HIGH)
    user.notification_time = time(9, 30)
    user.favourite_style = Style.CASUAL
    user.notifications_enabled = False
    user.season_notifications_enabled = True

    text = r.render_user_summary(user)

    assert "ник" in text.lower()
    assert "пол" in text.lower()
    assert "возраст" in text.lower()
    assert "город" in text.lower()
    assert "мерзлявость" in text.lower()
    assert "любимый стиль" in text.lower()
    assert "время уведомлений" in text.lower()
    assert "уведомления" in text.lower()
    assert "сезонные уведомления" in text.lower()


def test_manage_wardrobe_renderer_not_found() -> None:
    r = ManageWardrobeRenderer()

    result = ManageWardrobeResult(
        success=False,
        message_key="not_found",
        item=None,
    )

    msg = r.render(result)

    assert "не нашёл эту вещь" in msg.text.lower()

    callbacks = [b.callback_data
                 for row in msg.buttons for b in row]
    assert callbacks == ["wardrobe:open", "menu:home"]


def test_manage_wardrobe_renderer_deleted() -> None:
    r = ManageWardrobeRenderer()

    result = ManageWardrobeResult(
        success=True,
        message_key="deleted",
        item=None,
    )

    msg = r.render(result)

    assert "вещь удалена" in msg.text.lower()

    callbacks = [b.callback_data
                 for row in msg.buttons for b in row]
    assert callbacks == ["wardrobe:open", "menu:home"]


def test_manage_wardrobe_renderer_added() -> None:
    r = ManageWardrobeRenderer()

    item = make_item(
        item_id=1,
        category=ClothingCategory.TOP,
        subtype=ClothingSubtype.TSHIRT,
        warmth=WarmthLevel.MEDIUM,
    )

    result = ManageWardrobeResult(
        success=True,
        message_key="added",
        item=item,
    )

    msg = r.render(result)

    assert "вещь добавлена" in msg.text.lower()
    callbacks = [b.callback_data for row in msg.buttons for b in row]
    assert callbacks == ["wardrobe:add", "wardrobe:open", "menu:home"]


def test_manage_wardrobe_renderer_updated() -> None:
    r = ManageWardrobeRenderer()

    item = make_item(
        item_id=1,
        category=ClothingCategory.TOP,
        subtype=ClothingSubtype.TSHIRT,
        warmth=WarmthLevel.MEDIUM,
    )

    result = ManageWardrobeResult(
        success=True,
        message_key="updated",
        item=item,
    )

    msg = r.render(result)

    assert "вещь обновлена" in msg.text.lower()
    callbacks = [b.callback_data for row in msg.buttons for b in row]
    assert callbacks == ["wardrobe:open", "menu:home"]
