import pytest
from app.db.db_stage import *
from app.db.models import Stage
from app.db.db_queries import get_first_instance


@pytest.mark.asyncio
async def test_get_next_stage_existing(session: AsyncSession):
    """
    Test retrieval of the next stage after the current stage.
    Scenario: The current stage has a valid next stage.
    Expected: The correct next stage is returned.
    """
    current_stage = await get_first_instance(session, Stage, "id", story_id=2)
    next_stage = await get_next_stage(session, current_stage)

    assert next_stage is not None
    assert next_stage.level == current_stage.level + 1
    assert next_stage.name == "Second Challenge Indiana"  # Example name


@pytest.mark.asyncio
async def test_get_next_stage_nonexistent(session: AsyncSession):
    """
    Test retrieval of the next stage for the last stage of a story.
    Scenario: The current stage does not have a next stage.
    Expected: None is returned.
    """
    current_stage = await get_first_instance(
        session, Stage, "id", story_id=1, level=5
    )  # Assuming level 5 is the last
    next_stage = await get_next_stage(session, current_stage)

    assert next_stage is None
