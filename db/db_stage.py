from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Story, Stage
from db.db_queries import get_instance


async def get_next_stage(stage: Stage, db: AsyncSession):
    next_level = stage.level + 1
    next_stage = await get_instance(
        db, Stage, story_id=stage.story_id, level=next_level
    )
    if next_stage:
        return next_stage
