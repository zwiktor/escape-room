import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StoryAccess, User
from app.db.db_access import get_story_access, get_story_access_by_attempt


@pytest.mark.asyncio
async def test_get_story_access(session: AsyncSession, mock_user: User):
    # Pobierz przykładowego użytkownika i przygodę z danych testowych
    story_id = 1  # Zakładamy, że story_id 1 istnieje w test_data.json

    # Wywołanie testowanej funkcji
    story_access = await get_story_access(session, mock_user, story_id)

    # Sprawdzenie poprawności wyniku
    assert (
        story_access is not None
    ), "StoryAccess should exist for the given user and story_id."
    assert isinstance(
        story_access, StoryAccess
    ), "Returned object should be an instance of StoryAccess."
    assert story_access.user_id == mock_user.id, "User ID should match the given user."
    assert (
        story_access.story_id == story_id
    ), "Story ID should match the given story_id."


@pytest.mark.asyncio
async def test_get_story_access_nonexistent(session: AsyncSession, mock_user: User):
    # Pobierz przykładowego użytkownika i nieistniejącą przygodę
    story_id = 9999  # Zakładamy, że takie story_id nie istnieje

    # Wywołanie testowanej funkcji
    story_access = await get_story_access(session, mock_user, story_id)

    # Sprawdzenie poprawności wyniku
    assert (
        story_access is None
    ), "StoryAccess should not exist for the given user and non-existent story_id."


@pytest.mark.asyncio
async def test_get_story_access_by_attempt(session: AsyncSession, mock_user: User):
    # Pobierz przykładowego użytkownika i próbę z danych testowych
    attempt_id = 1  # Zakładamy, że attempt_id 1 istnieje w test_data.json

    # Wywołanie testowanej funkcji
    story_access = await get_story_access_by_attempt(session, attempt_id, mock_user)

    # Sprawdzenie poprawności wyniku
    assert (
        story_access is not None
    ), "StoryAccess should exist for the given user and attempt_id."
    assert isinstance(
        story_access, StoryAccess
    ), "Returned object should be an instance of StoryAccess."
    assert story_access.user.id == mock_user.id, "User ID should match the given user."


@pytest.mark.asyncio
async def test_get_story_access_by_attempt_nonexistent_attempt(
    session: AsyncSession, mock_user: User
):
    # Pobierz przykładowego użytkownika i nieistniejącą próbę
    attempt_id = 9999  # Zakładamy, że takie attempt_id nie istnieje

    # Wywołanie testowanej funkcji
    story_access = await get_story_access_by_attempt(session, attempt_id, mock_user)

    # Sprawdzenie poprawności wyniku
    assert (
        story_access is None
    ), "StoryAccess should not exist for the given user and non-existent attempt_id."


@pytest.mark.asyncio
async def test_get_story_access_by_attempt_invalid_user(
    session: AsyncSession, mock_user: User
):
    # Pobierz przykładową próbę i użytkownika, który nie ma dostępu
    attempt_id = 5  # Zakładamy, że attempt_id 1 istnieje w test_data.json

    # Wywołanie testowanej funkcji
    story_access = await get_story_access_by_attempt(session, attempt_id, mock_user)

    # Sprawdzenie poprawności wyniku
    assert (
        story_access is None
    ), "StoryAccess should not exist for a user without access."
