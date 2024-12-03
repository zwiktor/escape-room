import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_story import (
    get_all_stories,
    get_story_by_id,
    buy_story,
    start_story,
    create_story,
)
from db.models import Story
from schemas.story import StoryDisplay
from db.storymanager import StoryManager


@pytest.mark.asyncio
async def test_get_all_stories_success(session: AsyncSession):
    """Retrive all stories prepared with conftest 3 Stories"""
    stories = await get_all_stories(session)

    assert stories is not None

    assert stories[0].title == "Adventure Story"
    assert stories[2].difficulty == "Easy"
    assert all(isinstance(story, Story) for story in stories)


@pytest.mark.asyncio
async def test_get_story_existing(session: AsyncSession):
    """
    Test retrieval of a story by its ID.
    Scenario: The story exists in the database.
    Expected: The correct story object is returned.
    """
    story = await get_story_by_id(story_id=1, db=session)
    assert story is not None
    assert story.id == 1


@pytest.mark.asyncio
async def test_get_story_nonexistent(session: AsyncSession):
    """
    Test retrieval of a story by its ID when it does not exist.
    Scenario: The story ID does not match any records.
    Expected: None is returned.
    """
    story = await get_story_by_id(story_id=999, db=session)
    assert story is None


@pytest.mark.asyncio
async def test_create_story(session):
    """
    Test creation of a new story.
    Scenario: A valid StoryDisplay schema is provided.
    Expected: A new Story object is created in the database.
    """
    request = StoryDisplay(
        title="New Adventure",
        description="An exciting new adventure.",
        type="Adventure",
        difficulty="Easy",
        rating=4.5,
        cost=50,
    )
    story = await create_story(session, request)
    assert story is not None
    assert story.title == request.title
    assert story.description == request.description
    assert story.cost == request.cost


@pytest.mark.asyncio
async def test_buy_story_invalid_story(
    story_manager: StoryManager, session: AsyncSession
):
    """
    Test purchase of a non-existent story.
    """
    invalid_story_id = 9999  # Use a story ID that doesn't exist
    story_cost = 100  # Replace with the story's cost in gold

    # Call the method and expect a ValueError
    with pytest.raises(
        ValueError, match=f"Story with id {invalid_story_id} does not exist."
    ):
        await story_manager.buy_story(invalid_story_id, story_cost)
