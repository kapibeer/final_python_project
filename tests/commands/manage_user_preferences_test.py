# tests/commands/test_manage_user_preferences.py
import pytest

from commands.manage_user_preferences import ManageUserPreferences
from tests.helpers import FakeUserRepo, make_user


@pytest.mark.asyncio
async def test_update_preferences_returns_not_found_when_user_missing() \
        -> None:
    repo = FakeUserRepo(users=[])
    usecase = ManageUserPreferences(repo)

    res = await usecase.update_preferences(user_id=999, age=25)

    assert res.success is False
    assert res.message_key == "not_found"
    assert res.user is None
    assert repo.updated == []


@pytest.mark.asyncio
async def test_update_preferences_updates_existing_fields() -> None:
    user = make_user()
    repo = FakeUserRepo(users=[user])
    usecase = ManageUserPreferences(repo)

    res = await usecase.update_preferences(
        user_id=user.user_id,
        age=27,
        location="Amsterdam",
    )

    assert res.success is True
    assert res.message_key == "updated"
    assert res.user is not None
    assert res.user.age == 27
    assert res.user.location == "Amsterdam"
    assert len(repo.updated) == 1
    assert repo.updated[0].user_id == user.user_id


@pytest.mark.asyncio
async def test_update_preferences_ignores_unknown_fields() -> None:
    user = make_user()
    repo = FakeUserRepo(users=[user])
    usecase = ManageUserPreferences(repo)

    before_age = user.age

    # "no_such_field" не должен упасть и не должен ничего менять
    res = await usecase.update_preferences(
        user_id=user.user_id,
        no_such_field="xxx",  # type: ignore[arg-type]
    )

    assert res.success is True
    assert res.message_key == "updated"
    assert res.user is not None
    assert res.user.age == before_age
    assert len(repo.updated) == 1


@pytest.mark.asyncio
async def test_update_preferences_can_update_multiple_fields_at_once() -> None:
    user = make_user()
    repo = FakeUserRepo(users=[user])
    usecase = ManageUserPreferences(repo)

    res = await usecase.update_preferences(
        user_id=user.user_id,
        age=30,
        notifications_enabled=False,
        season_notifications_enabled=False,
    )

    assert res.success is True
    assert res.user is not None
    assert res.user.age == 30
    assert res.user.notifications_enabled is False
    assert res.user.season_notifications_enabled is False
    assert len(repo.updated) == 1
