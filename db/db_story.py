from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt
from schemas.story import StoryDisplay


async def get_instance(session: AsyncSession, model, **kwargs):
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance


async def get_or_create(session: AsyncSession, model, **kwargs):
    instance = await get_instance(session, model, **kwargs)
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
    return instance


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
    #stage = await first_stage(db, story_id)
    story_access = await get_or_create(session=db, model=StoryAccess, story_id=story_id,
                                         user_id=user.id)
    await db.refresh(story_access, attribute_names=['story'])
    return story_access.story
    # attempt = Attempt(
    #     story_access_id=story_access.id,
    #     stage_id=first_stage
    # )
    #
    # db.add(attempt)
    # await db.commit()

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





