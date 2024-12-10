import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Story, StoryAccess, Attempt, HintsAttempt, Hint
from db.storymanager import StoryManager
from schemas.access import StatusEnum, StoryStatus, StoryAccessBase, AttemptBase
from schemas.attempt import HintBase, HintsDisplay, PasswordCheckDisplay

from exceptions.exceptions import (
    EntityDoesNotExistError,
    StoryAlreadyStartedError,
    StoryAlreadyOwnedError,
    InsufficientGoldError,
    ServiceError,
)


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
    with pytest.raises(EntityDoesNotExistError):
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
        EntityDoesNotExistError, match=f"Attempt - {invalid_attempt_id} does not exist"
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
    with pytest.raises(
        EntityDoesNotExistError, match=f"Attempt - {attempt_id} does not exist"
    ):
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


@pytest.mark.asyncio
async def test_get_hints_valid_attempt(story_manager: StoryManager):
    """
    Test get_hints for a valid attempt with associated hints.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(1)

    # Call the method
    result = await story_manager.get_hints()

    # Validate the result
    assert isinstance(
        result, HintsDisplay
    ), "Result should be an instance of HintsDisplay."
    assert len(result.hints) > 0, "Hints should not be empty for a valid attempt."
    assert all(
        isinstance(hint, HintBase) for hint in result.hints
    ), "All items in hints should be instances of HintBase."
    assert (
        result.hints[0].text == "Add some numers"
    ), "Hint text should match the database data."
    assert (
        result.hints[0].trigger == "give me hint 3"
    ), "Hint trigger should match the database data."


@pytest.mark.asyncio
async def test_get_hints_no_hints(story_manager: StoryManager):
    """
    Test get_hints for a valid attempt with no associated hints.
    """
    # Set up the story_manager state
    await story_manager.load_by_story_id(2)
    result = await story_manager.get_hints()
    # Validate the result
    assert isinstance(
        result, HintsDisplay
    ), "Result should be an instance of HintsDisplay."
    assert (
        len(result.hints) == 0
    ), "Hints should be empty for an attempt with no associated hints."


@pytest.mark.asyncio
async def test_get_hints_no_attempt(story_manager: StoryManager):
    """
    Test get_hints when no current_attempt is set.
    """
    await story_manager.load_by_story_id(3)

    # Call the method and expect an exception
    with pytest.raises(
        AttributeError, match=".*'NoneType' object has no attribute 'id'.*"
    ):
        await story_manager.get_hints()


@pytest.mark.asyncio
async def test_buy_story_success(story_manager: StoryManager, session: AsyncSession):
    """
    Test successful purchase of a story.
    """
    await story_manager.load_by_story_id(6)

    # Set up the user's gold balance
    # Call the method
    await story_manager.buy_story()

    # Validate the result
    assert (
        story_manager.user.gold == 950
    ), "Gold should be deducted from the user's account."
    assert story_manager.story_access is not None, "StoryAccess should be created."
    assert (
        story_manager.story_status == StatusEnum.purchased
    ), "Story status should be 'purchased'."


@pytest.mark.asyncio
async def test_buy_story_insufficient_gold(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test purchase of a story when the user has insufficient gold.
    """
    await story_manager.load_by_story_id(7)

    # Call the method and expect a ValueError
    with pytest.raises(
        InsufficientGoldError, match="Insufficient gold to purchase the story."
    ):
        await story_manager.buy_story()


@pytest.mark.asyncio
async def test_buy_story_users_already_have_access(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test purchase of a story when the user has access to the story.
    """
    await story_manager.load_by_story_id(1)

    # Call the method and expect a ValueError
    with pytest.raises(StoryAlreadyOwnedError, match="User already owns this story."):
        await story_manager.buy_story()


@pytest.mark.asyncio
async def test_start_story_create_attempt(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test starting a story by creating the first attempt.
    """
    # Set up the StoryManager state
    await story_manager.load_by_story_id(8)
    await story_manager.start_story()

    assert (
        story_manager.current_attempt is not None
    ), "Current attempt should be created."
    assert (
        story_manager.current_attempt.id == 8 is not None
    ), "Current attempt should be created."
    assert (
        story_manager.current_attempt.stage_id == 11
    ), "Stage ID should match the story's first stage ID."
    assert (
        story_manager.story_status == StatusEnum.started
    ), "Story status should be 'started'."


@pytest.mark.asyncio
async def test_start_story_with_existing_attempt(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test starting a story when an active attempt already exists.
    """
    # Set up the StoryManager state
    await story_manager.load_by_story_id(1)

    with pytest.raises(
        StoryAlreadyStartedError, match="User has already started this story"
    ):
        await story_manager.start_story()


@pytest.mark.asyncio
async def test_start_story_no_access(story_manager: StoryManager):
    """
    Test starting a story when the user does not have access.
    """
    # Ensure the user does not have access
    await story_manager.load_by_story_id(9)

    # Call the method and expect a ValueError
    with pytest.raises(
        EntityDoesNotExistError, match="User does not have access to this story."
    ):
        await story_manager.start_story()


@pytest.mark.asyncio
async def test_validate_password_correct_password_with_next_stage(
    story_manager: StoryManager,
):
    """
    Test validate_password when the correct password unlocks the next stage.
    """
    password_attempt = "seek2"
    await story_manager.load_by_attempt_id(2)
    result = await story_manager.validate_password(password_attempt)

    # Validate the result
    assert (
        result.message == "Gratulacje, to prawidlowa odpowiedz"
    ), "Message should indicate the password was correct."
    assert (
        not result.new_hint
    ), "new_hint should be False when no new hint is triggered."
    assert (
        result.next_attempt == 8
    ), "next_attempt should contain the ID of the new attempt."
    assert not result.end_story, "end_story should be False for intermediate stages."
    assert isinstance(result, PasswordCheckDisplay)


@pytest.mark.asyncio
async def test_validate_password_correct_password_end_story(
    story_manager: StoryManager,
):
    """
    Test validate_password when the correct password ends the story.
    """
    password_attempt = "treasure 2"
    await story_manager.load_by_attempt_id(4)
    result = await story_manager.validate_password(password_attempt)

    # Validate the result
    assert (
        result.message == "Gratulacje, historia zostala zakonczona"
    ), "Message should indicate the story was completed."
    assert (
        not result.new_hint
    ), "new_hint should be False when no new hint is triggered."
    assert (
        result.next_attempt is None
    ), "next_attempt should be None at the end of the story."
    assert result.end_story, "end_story should be True when the story is completed."


@pytest.mark.asyncio
async def test_validate_password_incorrect_password_no_hint(
    story_manager: StoryManager,
):
    """
    Test validate_password when the password is incorrect and no hint is triggered.
    """
    # Mock dependencies
    password_attempt = "treasure 4"
    await story_manager.load_by_attempt_id(4)
    result = await story_manager.validate_password(password_attempt)

    # Validate the result
    assert (
        result.message == "Nieprawidłowa odpowiedź, próbuj dalej"
    ), "Message should indicate the stage is already solved for incorrect passwords."
    assert (
        not result.new_hint
    ), "new_hint should be False when no new hint is triggered."
    assert (
        result.next_attempt is None
    ), "next_attempt should be None for incorrect passwords."
    assert not result.end_story, "end_story should be False for incorrect passwords."


@pytest.mark.asyncio
async def test_validate_password_trigger_existing_hint(story_manager: StoryManager):
    """
    Test validate_password when the password triggers a new hint.
    """
    password_attempt = "give me hint 3"
    await story_manager.load_by_attempt_id(2)
    result = await story_manager.validate_password(password_attempt)

    # Validate the result
    assert (
        result.message == "Nieprawidłowa odpowiedź, próbuj dalej"
    ), "Message should indicate a new hint was discovered."
    assert (
        not result.new_hint
    ), "new_hint should be False when a hint was discovered eariler"
    assert (
        result.next_attempt is None
    ), "next_attempt should be None when a hint is triggered."
    assert not result.end_story, "end_story should be False when a hint is triggered."


@pytest.mark.asyncio
async def test_validate_password_trigger_hint(story_manager: StoryManager):
    """
    Test validate_password when the password triggers a new hint.
    """
    password_attempt = "give me hint 5"
    await story_manager.load_by_attempt_id(2)
    result = await story_manager.validate_password(password_attempt)

    # Validate the result
    assert (
        result.message == "Nowa wskazowka zostala odkryta"
    ), "Message should indicate a new hint was discovered."
    assert result.new_hint, "new_hint should be True when a hint is triggered."
    assert (
        result.next_attempt is None
    ), "next_attempt should be None when a hint is triggered."
    assert not result.end_story, "end_story should be False when a hint is triggered."
