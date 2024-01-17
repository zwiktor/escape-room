from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import Story, Stage
from schemas.story import StoryBase
from db.db_story import get_story


async def get_stages(request: StoryBase, stage_leve: int, db: AsyncSession):
    story = await get_story(request.id, db)
    await db.refresh(story, attribute_names=["stages"])
    stages = story.stages
    return stages


async def get_stage(request: StoryBase, stage_level: int, db: AsyncSession):
    story = await get_story(request.id, db)
    await db.refresh(story, attribute_names=["stages"])
    stages = story.stages[stage_level]
    return stages
