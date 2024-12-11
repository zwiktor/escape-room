import pytest
from app.db.models import *
from app.db.db_attempt import *
from app.db.db_queries import get_instance


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
async def test_get_hints_with_valid_attempt(session: AsyncSession, mock_user: User):
    """
    Test get_hints for a valid attempt with associated hints.
    """
    # Use an attempt_id that has hints in the test database
    valid_attempt_id = 2  # Replace with a valid attempt ID from test data

    # Call the function
    hints = await get_hints(db=session, attempt_id=valid_attempt_id)

    # Validate the results
    assert hints is not None, "Hints should be returned for a valid attempt_id."
    assert len(hints) > 0, "At least one hint should exist for the valid attempt_id."
    assert all(
        isinstance(hint, Hint) for hint in hints
    ), "All returned items should be instances of HintsAttempt."


@pytest.mark.asyncio
async def test_get_hints_with_no_hints(session: AsyncSession, mock_user: User):
    """
    Test get_hints for a valid attempt with no associated hints.
    """
    # Use an attempt_id that exists but has no hints in the test database
    attempt_id_with_no_hints = 3  # Replace with an attempt ID that has no hints

    # Call the function
    hints = await get_hints(db=session, attempt_id=attempt_id_with_no_hints)

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
    hints = await get_hints(db=session, attempt_id=invalid_attempt_id)

    # Validate the results
    assert hints == [], "Hints should be an empty list for a non-existent attempt_id."


@pytest.mark.asyncio
async def test_create_first_attempt(session: AsyncSession):
    """
    Test creating the first attempt for a story.
    Story 8, stage = 11, storyaccess = 7
    """
    story_access = await get_instance(
        session, StoryAccess, id=7
    )  # Replace with a valid

    # Call the function
    new_attempt = await create_first_attempt(db=session, story_access=story_access)

    # Validate the result
    assert new_attempt is not None, "The attempt should be created successfully."
    assert (
        new_attempt.story_access_id == story_access.id
    ), "StoryAccess ID should match."
    assert new_attempt.stage_id == 11, "Stage ID should match."
    assert new_attempt.start_date is not None, "Start date should be set."


@pytest.mark.asyncio
async def test_create_first_attempt_no_stage(session: AsyncSession):
    """
    Test creating the first attempt when no stages exist for the story.
    """
    # Ensure no stages exist for the story
    story_access = await get_instance(
        session, StoryAccess, id=8
    )  # Replace with a valid

    # Call the function and expect an exception
    with pytest.raises(ValueError, match="There is no stage for the Story"):
        await create_first_attempt(db=session, story_access=story_access)


@pytest.mark.asyncio
async def test_create_first_attempt_rollback(session: AsyncSession, mocker):
    """
    Test creating the first attempt with an invalid database session.
    """
    # Use an invalid session or close the session to simulate a database error
    story_access = await get_instance(session, StoryAccess, id=7)

    mocker.patch("app.db.db_attempt.Attempt", side_effect=Exception("Mocked Exception"))

    # Call the function and expect an exception
    with pytest.raises(
        Exception, match="Failed to create the first attempt: Mocked Exception"
    ):
        await create_first_attempt(db=session, story_access=story_access)
