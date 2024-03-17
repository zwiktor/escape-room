from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt
from schemas.story import StoryDisplay
from db.db_queries import get_instance, get_or_create


async def first_stage(db, story_id, level: int = 1):
    return await get_instance(session=db, model=Stage, story_id=story_id, level=level)


async def get_all_stories(db: AsyncSession):
    stmt = select(Story)
    all_stories = await db.scalars(stmt)

    return all_stories


async def get_story(story_id, db):
    stmt = select(Story).where(Story.id == story_id)

    return await db.scalar(stmt)


async def buy_story(db, story_id, user):
    story_access = await get_or_create(session=db, model=StoryAccess,
                                       story_id=story_id,
                                       user_id=user.id)
    await db.refresh(story_access, attribute_names=['story'])
    return story_access.story


async def create_story(db: AsyncSession, request: StoryDisplay):
    story = Story(
        title=request.title,
        description=request.description,
        type=request.type,
        difficulty=request.difficulty,
        rating=request.rating,
        cost=request.cost
    )

    db.add(story)
    await db.commit()

    return story
