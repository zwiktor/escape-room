import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Story, StoryAccess, Attempt
from db.storymanager import StoryManager
from schemas.access import StatusEnum


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
