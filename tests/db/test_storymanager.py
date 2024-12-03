import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Story, StoryAccess, Attempt
from db.storymanager import StoryManager
from schemas.access import StatusEnum, StoryStatus, StoryAccessBase, AttemptBase


@pytest.mark.asyncio
async def test_load_by_story_id_with_access(
    story_manager: StoryManager, session: AsyncSession
):
    """Test load_by_story_id for a user with access to the story."""
    story_id = 1
    story_access_id = 1

    # Call the method
    await story_manager.load_by_story_id(story_id)

    # Validate the state of StoryManager
    assert story_manager.story is not None, "Story should be loaded."
    assert story_manager.story.id == story_id, "Story ID should match the loaded story."
    assert story_manager.story_access is not None, "StoryAccess should be loaded."
    assert (
        story_manager.story_access.id == story_access_id
    ), "StoryAccess ID should match the loaded access."
    assert (
        story_manager.story_status == StatusEnum.started
    ), "Story status should be 'started'."


@pytest.mark.asyncio
async def test_load_by_story_id_without_access(
    story_manager: StoryManager, session: AsyncSession
):
    """Test load_by_story_id for a user without access to the story.
    Story is loaded to story manager but no access
    """
    story_id = 4

    # Call the method
    await story_manager.load_by_story_id(story_id)

    # Validate the state of StoryManager
    assert story_manager.story is not None, "Story should be loaded."
    assert story_manager.story.id == story_id, "Story ID should match the loaded story."
    assert (
        story_manager.story_access is None
    ), "StoryAccess should be None for a user without access."
    assert story_manager.story_status == StatusEnum.new, "Story status should be 'new'."


@pytest.mark.asyncio
async def test_load_by_story_id_without_access(
    story_manager: StoryManager, session: AsyncSession
):
    """Test load_by_story_id for a user without access to the story.
    Story is loaded to story manager but no access
    """
    story_id = 5
    # Call the method
    await story_manager.load_by_story_id(story_id)

    # Validate the state of StoryManager
    assert story_manager.story is not None, "Story should be loaded."
    assert story_manager.story.id == story_id, "Story ID should match the loaded story."
    assert (
        story_manager.story_access is None
    ), "StoryAccess should be None for a user without access."
    assert story_manager.story_status == StatusEnum.new, "Story status should be 'new'."


@pytest.mark.asyncio
async def test_load_by_story_id_with_invalid_story_id(
    story_manager: StoryManager, session: AsyncSession
):
    """Test load_by_story_id for a user without access to the story.
    Story is loaded to story manager but no access
    """
    story_id = 9999

    # Call the method chach error if storyid is invalid
    with pytest.raises(ValueError):
        await story_manager.load_by_story_id(story_id)


@pytest.mark.asyncio
async def test_load_by_attempt_id_valid(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test load_by_attempt_id with a valid attempt ID.
    """
    attempt_id = 2
    story_access_id = 1

    # Call the method
    await story_manager.load_by_attempt_id(attempt_id)

    # Validate the state of StoryManager
    assert (
        story_manager.current_attempt is not None
    ), "Current Attempt should be loaded."
    assert (
        story_manager.current_attempt.id == attempt_id
    ), "Attempt ID should match the loaded attempt."
    assert story_manager.story_access is not None, "StoryAccess should be loaded."
    assert (
        story_manager.story_access.id == story_access_id
    ), "StoryAccess ID should match the Attempt's access ID."
    assert story_manager.story is not None, "Story should be loaded."
    assert (
        story_manager.story.id == story_manager.story_access.story_id
    ), "Story ID should match the StoryAccess's story_id."
    assert (
        story_manager.story_status == StatusEnum.started
    ), "Story status should be 'started'."


@pytest.mark.asyncio
async def test_load_by_attempt_id_resolved_but_not_active(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test load_by_attempt_id with a resolved attempt ID. This is a try to load not active attempt
    It should move user to active one
    """
    attempt_id = 1
    story_access_id = 1

    # Call the method
    await story_manager.load_by_attempt_id(attempt_id)

    # Validate the state of StoryManager
    assert (
        story_manager.current_attempt is not None
    ), "Current Attempt should be loaded."
    assert (
        story_manager.current_attempt.id != attempt_id
    ), "Attempt Id is diffrent from current active attempt"
    assert story_manager.attempt_finished == True


@pytest.mark.asyncio
async def test_load_by_attempt_id_finished_attempt(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test load_by_attempt_id with a finished attempt (attempt with a finish_date).
    """
    attempt_id = 7  # Replace with a valid attempt_id for a finished attempt
    story_access_id = 6  # Replace with the story_access_id linked to this attempt

    # Call the method
    await story_manager.load_by_attempt_id(attempt_id)

    # Validate the state of StoryManager
    assert (
        story_manager.current_attempt is not None
    ), "Current Attempt should be loaded."
    assert (
        story_manager.current_attempt.id == attempt_id
    ), "Attempt ID should match the loaded attempt."
    assert (
        story_manager.current_attempt.finish_date is not None
    ), "Finish date should be set for a finished attempt."
    assert story_manager.story_access is not None, "StoryAccess should be loaded."
    assert (
        story_manager.story_access.id == story_access_id
    ), "StoryAccess ID should match the Attempt's access ID."
    assert story_manager.story is not None, "Story should be loaded."
    assert (
        story_manager.story_status == StatusEnum.ended
    ), "Story status should be 'ended'."


@pytest.mark.asyncio
async def test_load_by_attempt_id_invalid_attempt(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test load_by_attempt_id with an invalid attempt ID.
    """
    invalid_attempt_id = 9999  # Non-existent attempt ID

    # Call the method and expect a ValueError
    with pytest.raises(
        ValueError, match=f"Attempt - {invalid_attempt_id} does not exist"
    ):
        await story_manager.load_by_attempt_id(invalid_attempt_id)


@pytest.mark.asyncio
async def test_load_by_attempt_id_no_access(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test load_by_attempt_id for an attempt where the user has no access.
    """
    attempt_id = 5

    # Call the method and expect a ValueError
    with pytest.raises(ValueError, match=f"Attempt - {attempt_id} does not exist"):
        await story_manager.load_by_attempt_id(attempt_id)


@pytest.mark.asyncio
async def test_check_access_new_story(story_manager: StoryManager):
    """
    Test check_access when the story_status is 'new'.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(5)

    # Call the method
    result = await story_manager.check_access()

    # Validate the result
    assert isinstance(
        result, StoryStatus
    ), "Result should be an instance of StoryStatus."
    assert result.status == StatusEnum.new, "Status should be 'new'."
    assert result.story_access is None, "StoryAccess should be None for a new story."


@pytest.mark.asyncio
async def test_check_access_purchased_story(story_manager: StoryManager):
    """
    Test check_access when the story_status is 'purchased'.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(3)

    # Call the method
    result = await story_manager.check_access()

    # Validate the result
    assert isinstance(
        result, StoryStatus
    ), "Result should be an instance of StoryStatus."
    assert result.status == StatusEnum.purchased, "Status should be 'purchased'."
    assert isinstance(
        result.story_access, StoryAccessBase
    ), "StoryAccess should be an instance of StoryAccessBase."


@pytest.mark.asyncio
async def test_check_access_started_story(story_manager: StoryManager):
    """
    Test check_access when the story_status is 'started'.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(1)

    result = await story_manager.check_access()

    # Validate the result
    assert isinstance(
        result, StoryStatus
    ), "Result should be an instance of StoryStatus."
    assert result.status == StatusEnum.started, "Status should be 'started'."
    assert isinstance(
        result.story_access, StoryAccessBase
    ), "StoryAccess should be an instance of StoryAccessBase."
    assert isinstance(
        result.story_access.current_attempt, AttemptBase
    ), "Current attempt should be an instance of AttemptBase."
    assert (
        result.story_access.current_attempt.finish_date is None
    ), "Current attempt should be an instance of AttemptBase."


@pytest.mark.asyncio
async def test_check_access_ended_story(story_manager: StoryManager):
    """
    Test check_access when the story_status is 'ended'.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(4)

    # Call the method
    result = await story_manager.check_access()

    # Validate the result
    assert isinstance(
        result, StoryStatus
    ), "Result should be an instance of StoryStatus."
    assert result.status == StatusEnum.ended, "Status should be 'ended'."
    assert isinstance(
        result.story_access, StoryAccessBase
    ), "StoryAccess should be an instance of StoryAccessBase."
    assert isinstance(
        result.story_access.current_attempt, AttemptBase
    ), "Current attempt should be an instance of AttemptBase."
    assert result.story_access.current_attempt is not None
