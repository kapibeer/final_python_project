from __future__ import annotations

from typing import Optional, List, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.clothing_item import (
    ClothingItem,
    ClothingCategory,
    Color,
    Style,
    WarmthLevel,
    ClothingSubtype,
)
from domain.repositories.wardrobe_repository import WardrobeRepository
from adapters.database_adapters.models.wardrobe_table import WardrobeTable


class DBWardrobeRepository(WardrobeRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    # -------------------- mapping --------------------

    @staticmethod
    def _to_domain(row: WardrobeTable) -> ClothingItem:
        return ClothingItem(
            item_id=row.item_id,
            owner_id=row.owner_id,
            image_id=row.image_id,
            name=row.name,
            category=ClothingCategory(row.category),
            main_color=Color(row.main_color),
            style=Style(row.style),
            warmth_level=WarmthLevel(row.warmth_level),
            subtype=ClothingSubtype(row.subtype),
            is_waterproof=row.is_waterproof,  # type: ignore
            is_windproof=row.is_windproof,  # type: ignore
        )
        # top_group выставится сам в __post_init__

    @staticmethod
    def _apply_domain_to_row(row: WardrobeTable, item: ClothingItem) -> None:
        row.owner_id = item.owner_id
        row.image_id = item.image_id
        row.name = item.name

        row.category = item.category.value
        row.main_color = item.main_color.value
        row.style = item.style.value
        row.warmth_level = item.warmth_level.value
        row.subtype = item.subtype.value

        row.is_waterproof = item.is_waterproof
        row.is_windproof = item.is_windproof

    # -------------------- protocol methods --------------------

    async def get_user_wardrobe(self, user_id: int) -> List[ClothingItem]:
        async with self._session_factory() as s:
            stmt = select(WardrobeTable). \
                where(WardrobeTable.owner_id == user_id)
            rows = (await s.execute(stmt)).scalars().all()  # type: ignore
            return [self._to_domain(r) for r in rows]  # type: ignore

    async def get_item(self, user_id: int, item_id: int) \
            -> Optional[ClothingItem]:
        async with self._session_factory() as s:
            stmt = select(WardrobeTable).where(
                WardrobeTable.item_id == item_id,
                WardrobeTable.owner_id == user_id,
            )
            row = (await s.execute(stmt)).scalars().first()  # type: ignore
            return self._to_domain(row) if row else None  # type: ignore

    async def add_item(self, user_id: int, item: ClothingItem) -> int:
        async with self._session_factory() as s:
            row = WardrobeTable(owner_id=user_id)
            self._apply_domain_to_row(row, item)

            await s.add(row)  # type: ignore
            await s.commit()
            await s.refresh(row)

            return row.item_id

    async def update_item(self, user_id: int, item: ClothingItem) -> None:
        # защищаемся, чтобы нельзя было обновить чужую вещь
        async with self._session_factory() as s:
            row = s.get(WardrobeTable, item.item_id)
            if row is None or row.owner_id != user_id:  # type: ignore
                return

            self._apply_domain_to_row(row, item)  # type: ignore
            await s.commit()

    async def delete_item(self, user_id: int, item_id: int) -> None:
        async with self._session_factory() as s:
            stmt = select(WardrobeTable).where(
                WardrobeTable.item_id == item_id,
                WardrobeTable.owner_id == user_id,
            )
            row = (await s.execute(stmt)).scalars().first()  # type: ignore
            if row is None:
                return

            await s.delete(row)  # type: ignore
            await s.commit()
