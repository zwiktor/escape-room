import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_story import get_all_stories, get_story, buy_story, start_story, create_story
from db.models import Story
from schemas.story import StoryDisplay


@pytest.mark.asyncio
async def test_get_all_stories_success(session: AsyncSession):
    """Retrive all stories prepared with conftest 3 Stories"""
    stories = await get_all_stories(session)

    assert stories is not None

    assert len(stories) == 4
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
    story = await get_story(story_id=1, db=session)
    assert story is not None
    assert story.id == 1


@pytest.mark.asyncio
async def test_get_story_nonexistent(session: AsyncSession):
    """
    Test retrieval of a story by its ID when it does not exist.
    Scenario: The story ID does not match any records.
    Expected: None is returned.
    """
    story = await get_story(story_id=999, db=session)
    assert story is None


@pytest.mark.asyncio
async def test_buy_story_existing_access(session: AsyncSession, mock_user):
    """
    Test purchasing a story for a user who already has access.
    Scenario: The user has already purchased the story.
    Expected: The existing StoryAccess object is returned.
    """
    story_access = await buy_story(session, story_id=1, user=mock_user)
    assert story_access is not None
    assert story_access.story_id == 1
    assert story_access.user_id == mock_user.id


@pytest.mark.asyncio
async def test_buy_story_new_access(session: AsyncSession, mock_user):
    """
    Test purchasing a story for a user who does not have access.
    Scenario: The user has not purchased the story yet.
    Expected: A new StoryAccess object is created and returned.
    """
    story_access = await buy_story(session, story_id=3, user=mock_user)
    assert story_access is not None
    assert story_access.story_id == 3
    assert story_access.user_id == mock_user.id


@pytest.mark.asyncio
async def test_start_story_existing_access_and_attempt(
    session: AsyncSession, mock_user
):
    """
    Test starting a story for a user who has access and an existing attempt.
    Scenario: The user has already started the story.
    Expected: The existing Attempt object is returned.
    """
    attempt = await start_story(session, story_id=1, user=mock_user)
    assert attempt is not None
    assert attempt.story_access_id == 1
    assert attempt.stage_id == 1


@pytest.mark.asyncio
async def test_start_story_new_access_and_attempt(session: AsyncSession, mock_user):
    """
    Test starting a story for a user who has no access and no existing attempt.
    Scenario: The user starts the story for the first time.
    Expected: A new StoryAccess and Attempt object are created and returned.
    """
    attempt = await start_story(session, story_id=2, user=mock_user)
    assert attempt is not None
    assert attempt.story_access_id is not None
    assert attempt.stage_id is not None


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
