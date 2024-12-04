from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt
from schemas.story import StoryDisplay
from db.db_queries import get_instance, get_or_create, create_instance, get_instances


async def get_all_stories(db: AsyncSession):
    all_stories = await get_instances(db, Story)

    return all_stories


async def get_story_by_id(db: AsyncSession, story_id: int):
    stmt = select(Story).where(Story.id == story_id)

    return await db.scalar(stmt)


async def create_story(db: AsyncSession, request: StoryDisplay):
    story = await create_instance(
        db,
        Story,
        title=request.title,
        description=request.description,
        type=request.type,
        difficulty=request.difficulty,
        rating=request.rating,
        cost=request.cost,
    )

    return story
