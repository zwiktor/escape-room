from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Stage, Attempt
from app.db.db_queries import get_instance


async def get_next_stage(db: AsyncSession, stage: Stage):
    next_level = stage.level + 1
    next_stage = await get_instance(
        db, Stage, story_id=stage.story_id, level=next_level
    )
    if next_stage:
        return next_stage


async def get_stage_by_attempt(db: AsyncSession, attempt: Attempt) -> Stage:
    return await get_instance(db, Stage, id=attempt.stage_id)
