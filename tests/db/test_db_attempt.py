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


@pytest.mark.asyncio
async def test_get_hints_with_valid_attempt(session: AsyncSession, mock_user: User):
    """
    Test get_hints for a valid attempt with associated hints.
    """
    # Use an attempt_id that has hints in the test database
    valid_attempt_id = 1  # Replace with a valid attempt ID from test data

    # Call the function
    hints = await get_hints(valid_attempt_id, db=session)

    # Validate the results
    assert hints is not None, "Hints should be returned for a valid attempt_id."
    assert len(hints) > 0, "At least one hint should exist for the valid attempt_id."
    assert all(
        isinstance(hint, HintsAttempt) for hint in hints
    ), "All returned items should be instances of HintsAttempt."


@pytest.mark.asyncio
async def test_get_hints_with_no_hints(session: AsyncSession, mock_user: User):
    """
    Test get_hints for a valid attempt with no associated hints.
    """
    # Use an attempt_id that exists but has no hints in the test database
    attempt_id_with_no_hints = 2  # Replace with an attempt ID that has no hints

    # Call the function
    hints = await get_hints(attempt_id_with_no_hints, db=session)

    # Validate the results
    assert (
        hints == []
    ), "Hints should be an empty list for an attempt_id with no associated hints."


@pytest.mark.asyncio
async def test_get_hints_with_invalid_attempt(session: AsyncSession, mock_user: User):
    """
    Test get_hints for an invalid attempt_id.
    """
    # Use an invalid attempt_id that doesn't exist in the test database
    invalid_attempt_id = 9999  # Non-existent attempt ID

    # Call the function
    hints = await get_hints(invalid_attempt_id, db=session)

    # Validate the results
    assert hints == [], "Hints should be an empty list for a non-existent attempt_id."
