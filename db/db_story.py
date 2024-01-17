from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Story
from schemas.story import StoryDisplay


async def get_all_stories(db: AsyncSession):
    stmt = select(Story)
    all_stories = await db.scalars(stmt)

    return all_stories


async def get_story(story_id, db):
    stmt = select(Story).where(Story.id == story_id)

    return await db.scalar(stmt)


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





