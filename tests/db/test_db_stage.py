import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_stage import *
from db.models import Stage, Story
from schemas.story import StoryDisplay


@pytest.mark.asyncio
async def test_get_next_stage_existing(session: AsyncSession):
    """
    Test retrieval of the next stage after the current stage.
    Scenario: The current stage has a valid next stage.
    Expected: The correct next stage is returned.
    """
    current_stage = await first_stage(session, story_id=1, level=1)
    next_stage = await get_next_stage(current_stage, session)

    assert next_stage is not None
    assert next_stage.level == current_stage.level + 1
    assert next_stage.name == "Second Challenge"  # Example name


@pytest.mark.asyncio
async def test_get_next_stage_nonexistent(session: AsyncSession):
    """
    Test retrieval of the next stage for the last stage of a story.
    Scenario: The current stage does not have a next stage.
    Expected: None is returned.
    """
    current_stage = await first_stage(
        session, story_id=1, level=5
    )  # Assuming level 5 is the last
    next_stage = await get_next_stage(current_stage, session)

    assert next_stage is None
