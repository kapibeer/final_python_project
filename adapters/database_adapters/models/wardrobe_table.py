# database_adapters/models/wardrobe_table.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WardrobeTable(Base):
    __tablename__ = "wardrobe_items"

    item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                         autoincrement=True)

    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    image_id: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)

    category: Mapped[str] = mapped_column(String(32),
                                          nullable=False)
    main_color: Mapped[str] = mapped_column(String(32),
                                            nullable=False)
    style: Mapped[str] = mapped_column(String(32),
                                       nullable=False,
                                       default="casual")
    warmth_level: Mapped[str] = mapped_column(String(32),
                                              nullable=False,
                                              default="medium")
    subtype: Mapped[str] = mapped_column(String(64),
                                         nullable=False,
                                         default="tshirt")

    is_waterproof: Mapped[Optional[bool]] = mapped_column(Boolean,
                                                          nullable=True)
    is_windproof: Mapped[Optional[bool]] = mapped_column(Boolean,
                                                         nullable=True)
