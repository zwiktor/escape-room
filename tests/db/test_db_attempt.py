import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import *
from db.db_attempt import *
from db.db_queries import get_instance, get_or_create, get_last_instance
from schemas.attempt import AttemptDisplay
from schemas.stage import StageDisplay


@pytest.mark.asyncio
async def test_get_active_attempt(session: AsyncSession, mock_user: User):
    # Assume story_access_id exists in test data
    story_access_id = 1  # Example ID for StoryAccess

    # Call the function to test
    active_attempt = await get_active_attempt(session, story_access_id)

    # Validate the result
    assert (
        active_attempt is not None
    ), "Active attempt should be returned for a valid story_access_id."
    assert isinstance(
        active_attempt, Attempt
    ), "Returned object should be an instance of Attempt."
    assert (
        active_attempt.story_access_id == story_access_id
    ), "StoryAccess ID should match the provided ID."


@pytest.mark.asyncio
async def test_get_active_attempt_no_attempt(session: AsyncSession, mock_user: User):
    # Use a story_access_id that doesn't have any associated attempts
    story_access_id = 9999  # Example of a non-existent or unused ID

    # Call the function to test
    active_attempt = await get_active_attempt(session, story_access_id)

    # Validate the result
    assert (
        active_attempt is None
    ), "No active attempt should be returned for a non-existent story_access_id."


@pytest.mark.asyncio
async def test_get_attempt_invalid_id(session: AsyncSession, mock_user: User):
    """
    Test case for an invalid attempt ID.
    Expected: None or an exception is raised.
    """
    invalid_attempt_id = 999  # Nieistniejący attempt_id
    with pytest.raises(Exception):  # Oczekiwanie odpowiedniego wyjątku
        await get_attempt(attempt_id=invalid_attempt_id, db=session)
