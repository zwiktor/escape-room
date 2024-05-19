from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import Story, Stage
from schemas.story import StoryBase
from db.db_story import get_story
from db.db_queries import get_instance


async def get_stages(request: StoryBase, db: AsyncSession):
    story = await get_story(request.id, db)
    await db.refresh(story, attribute_names=["stages"])
    stages = story.stages
    return stages


async def get_stage(request: StoryBase, stage_level: int, db: AsyncSession):
    story = await get_story(request.id, db)
    await db.refresh(story, attribute_names=["stages"])
    stages = story.stages[stage_level]
    return stages


async def get_next_stage(stage: Stage, db: AsyncSession):
    next_level = stage.level + 1
    next_stage = await get_instance(db, Stage, story_id=stage.story_id, level=next_level)
    if next_stage:
        return next_stage