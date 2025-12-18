from __future__ import annotations

from typing import Optional, List
from datetime import time

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from domain import User, ColdSensitivity, Season, Style
from domain.repositories.user_repository import UserRepository
from database_adapters.models.user_table import UserTable


class DBUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    # -------------------- mapping --------------------

    @staticmethod
    def _to_domain(row: UserTable) -> User:
        return User(
            user_id=row.user_id,
            username=row.username,
            gender=row.gender,
            age=row.age,
            location=row.location,
            cold_sensitivity=ColdSensitivity(row.cold_sensitivity),
            notification_time=row.notification_time,
            notifications_enabled=row.notifications_enabled,
            season_notifications_enabled=row.season_notifications_enabled,
            last_season_notifiied=Season(row.last_season_notifiied)
            if row.last_season_notifiied else None,
            favourite_style=Style(row.favourite_style),
        )

    @staticmethod
    def _apply_domain_to_row(row: UserTable, user: User) -> None:
        row.username = user.username
        row.gender = user.gender
        row.age = user.age
        row.location = user.location

        row.cold_sensitivity = user.cold_sensitivity.value
        row.notification_time = user.notification_time
        row.notifications_enabled = user.notifications_enabled
        row.season_notifications_enabled = user.season_notifications_enabled

        row.last_season_notifiied = (
            user.last_season_notifiied.value
            if user.last_season_notifiied else None
        )

        row.favourite_style = user.favourite_style.value

    # -------------------- protocol methods --------------------

    def get(self, user_id: int) -> Optional[User]:
        row = self._session.get(UserTable, user_id)
        return self._to_domain(row) if row else None

    def create(self, user: User) -> None:
        row = UserTable(user_id=user.user_id)  # PK задаём сами
        self._apply_domain_to_row(row, user)
        self._session.add(row)
        self._session.commit()

    def update(self, user: User) -> None:
        row = self._session.get(UserTable, user.user_id)
        if row is None:
            return
        self._apply_domain_to_row(row, user)
        self._session.commit()

    def delete(self, user_id: int) -> None:
        row = self._session.get(UserTable, user_id)
        if row is None:
            return
        self._session.delete(row)
        self._session.commit()

    def get_or_create(self, user: User) -> User:
        existing = self.get(user.user_id)
        if existing is not None:
            return existing
        self.create(user)
        return user

    def get_all_users_with_seasonal_notifications(self) -> List[User]:
        stmt = select(UserTable).where(
            UserTable.season_notifications_enabled.is_(True)
        )
        rows = self._session.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in rows]

    def get_users_to_notify_between(self, start: time, end: time) \
            -> list[User]:
        stmt = select(UserTable).\
            where(UserTable.notifications_enabled.is_(True))

        if start <= end:
            # обычный случай: 09:55..10:00
            stmt = stmt.where(
                and_(UserTable.notification_time >= start,
                     UserTable.notification_time <= end)
            )
        else:
            # окно пересекает полночь: 23:58..00:03
            stmt = stmt.where(
                (UserTable.notification_time >= start) |
                (UserTable.notification_time <= end)
            )

        rows = self._session.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in rows]
