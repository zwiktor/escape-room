import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Story, Stage, StoryAccess, Attempt, User
from db.db_queries import get_instance, get_or_create, get_last_instance
from db.db_access import check_status
from schemas.access import *


@pytest.mark.asyncio
async def test_check_status_new_story(session: AsyncSession, mock_user: User):
    """
    Test case for a new story without any access or attempts.
    Expected: Status is 'new' with no access or attempts.
    """
    result = await check_status(
        db=session, user=mock_user, story_id=4
    )  # Non-existing story_id
    assert result == {
        "status": "new",
        "story_access": {"purchase_date": None, "current_attempt": None},
    }


@pytest.mark.asyncio
async def test_check_status_purchased_story(session: AsyncSession, mock_user: User):
    """
    Test case for a purchased story without any attempts.
    Expected: Status is 'purchased' with the purchase date set.
    """
    result = await check_status(
        db=session, user=mock_user, story_id=3
    )  # Existing story_id
    assert result["status"] == "purchased"
    assert result["story_access"]["purchase_date"] is not None
    assert result["story_access"]["current_attempt"] is None


@pytest.mark.asyncio
async def test_check_status_started_story(session: AsyncSession, mock_user: User):
    """
    Test case for a story that has been started but not finished.
    Expected: Status is 'started' with the current attempt data.
    """
    result = await check_status(
        db=session, user=mock_user, story_id=2
    )  # Started story_id
    assert result["status"] == "started"
    assert result["story_access"]["purchase_date"] is not None
    assert result["story_access"]["current_attempt"] is not None
    assert result["story_access"]["current_attempt"].finish_date is None


@pytest.mark.asyncio
async def test_check_status_finished_story(session: AsyncSession, mock_user: User):
    """
    Test case for a story that has been started and finished.
    Expected: Status is 'finished' with the current attempt data.
    """
    result = await check_status(
        db=session, user=mock_user, story_id=1
    )  # Finished story_id
    assert result["status"] == "finished"
    assert result["story_access"]["purchase_date"] is not None
    assert result["story_access"]["current_attempt"] is not None
    assert result["story_access"]["current_attempt"].finish_date is not None


@pytest.mark.asyncio
async def test_check_status_user_no_access(session: AsyncSession, mock_user: User):
    """
    Test case where user has no access to the story.
    Expected: Status is 'new' with no access or attempts.
    """
    result = await check_status(
        db=session, user=mock_user, story_id=999
    )  # Non-purchased story
    assert result is None
