import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_stage import *
from db.models import Stage, Story
from schemas.story import StoryDisplay


@pytest.mark.asyncio
async def test_get_stages_existing_story(session):
    """
    Test retrieval of all stages for an existing story.
    Scenario: The story has multiple stages.
    Expected: A list of stages associated with the story is returned.
    """
    story_request = StoryBase(id=1)
    stages = await get_stages(story_request, session)

    assert isinstance(stages, list)
    assert len(stages) > 0
    assert all(isinstance(stage, Stage) for stage in stages)


@pytest.mark.asyncio
async def test_get_stages_nonexistent_story(session):
    """
    Test retrieval of stages for a non-existent story.
    Scenario: The story does not exist in the database.
    Expected: The function raises an exception or returns None.
    """
    story_request = StoryBase(id=999)
    with pytest.raises(Exception):  # Adjust the exception type based on actual behavior
        await get_stages(story_request, session)
