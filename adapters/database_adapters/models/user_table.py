from __future__ import annotations

from datetime import time
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Time, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserTable(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)

    gender: Mapped[str] = mapped_column(String(32), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)

    cold_sensitivity: Mapped[str] = mapped_column(String(32), nullable=False,
                                                  default="medium")

    notification_time: Mapped[time] = mapped_column(Time, nullable=False,
                                                    default=time(hour=10,
                                                                 minute=0))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean,
                                                        nullable=False,
                                                        default=True)
    season_notifications_enabled: Mapped[bool] = mapped_column(Boolean,
                                                               nullable=False,
                                                               default=True)

    last_season_notifiied: Mapped[Optional[str]] = mapped_column(String(32),
                                                                 nullable=True)

    favourite_style: Mapped[str] = mapped_column(String(32), nullable=False,
                                                 default="casual")
