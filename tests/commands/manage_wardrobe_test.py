import pytest

from commands.manage_wardrobe import ManageWardrobe
from tests.helpers import FakeWardrobeRepo, make_item
from domain.models.clothing_item import (
    ClothingCategory,
    ClothingSubtype,
    WarmthLevel,
)

pytestmark = pytest.mark.asyncio


async def test_add_item_success():
    repo = FakeWardrobeRepo()
    usecase = ManageWardrobe(repo)

    item = make_item(
        item_id=1,
        category=ClothingCategory.TOP,
        subtype=ClothingSubtype.TSHIRT,
    )

    result = await usecase.add_item(user_id=1, item=item)

    assert result.success is True
    assert result.message_key == "added"
    assert result.item == item
    assert len(repo.added) == 1


async def test_update_item_not_found():
    repo = FakeWardrobeRepo()
    usecase = ManageWardrobe(repo)

    result = await usecase.update_item(
        user_id=1,
        item_id=999,
        name="new name",
    )

    assert result.success is False
    assert result.message_key == "not_found"
    assert result.item is None


async def test_update_item_success():
    item = make_item(
        item_id=1,
        category=ClothingCategory.TOP,
        subtype=ClothingSubtype.TSHIRT,
        warmth=WarmthLevel.LIGHT,
    )

    repo = FakeWardrobeRepo(items=[item])
    usecase = ManageWardrobe(repo)

    result = await usecase.update_item(
        user_id=1,
        item_id=1,
        name="Updated name",
        warmth_level=WarmthLevel.WARM,
    )

    assert result.success is True
    assert result.message_key == "updated"
    assert result.item.name == "Updated name"  # type: ignore
    assert result.item.warmth_level == WarmthLevel.WARM  # type: ignore
    assert len(repo.updated) == 1


async def test_delete_item_not_found():
    repo = FakeWardrobeRepo()
    usecase = ManageWardrobe(repo)

    result = await usecase.delete_item(user_id=1, item_id=123)

    assert result.success is False
    assert result.message_key == "not_found"


async def test_delete_item_success():
    item = make_item(
        item_id=1,
        category=ClothingCategory.BOTTOM,
        subtype=ClothingSubtype.JEANS,
    )

    repo = FakeWardrobeRepo(items=[item])
    usecase = ManageWardrobe(repo)

    result = await usecase.delete_item(user_id=1, item_id=1)

    assert result.success is True
    assert result.message_key == "deleted"
    assert 1 in repo.deleted
