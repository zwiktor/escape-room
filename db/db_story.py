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
    """
    Powinna być dodana logika z kupowaniem przygód za monedy/punkty
    :param db:
    :param story_id:
    :param user:
    :return:
    """
    story_access = await get_or_create(
        session=db, model=StoryAccess, story_id=story_id, user_id=user.id
    )
    return story_access


async def start_story(db, story_id, user):
    stage = await get_instance(db, Stage, story_id=story_id, level=1)
    story_access = await buy_story(db, story_id, user)
    attempt = await get_or_create(
        session=db, model=Attempt, story_access_id=story_access.id, stage_id=stage.id
    )

    return attempt


async def create_story(db: AsyncSession, request: StoryDisplay):
    story = Story(
        title=request.title,
        description=request.description,
        type=request.type,
        difficulty=request.difficulty,
        rating=request.rating,
        cost=request.cost,
    )

    db.add(story)
    await db.commit()

    return story
