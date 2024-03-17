from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt

from db.db_queries import get_instance, get_or_create
from db.models import User


async def get_access(db: AsyncSession, user: User, story_id: int):
    return await get_instance(session=db, model=StoryAccess, story_id=story_id, user_id=user.id)


async def current_attempt(db: AsyncSession, user: User, story_access: StoryAccess, level: int = 1):

    stage = await get_instance(session=db, model=Stage, story_id=story_access.story_id,
                               level=level)

    attempt = await get_or_create(session=db, model=Attempt, story_access_id=story_access.id,
                                  stage_id=stage.id, finished_date=null)
    return attempt

