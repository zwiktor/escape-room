from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    User,
    Attempt,
    HintsAttempt,
)
from db.db_queries import (
    get_instance,
    get_instances,
    get_last_instance,
)


async def get_active_attempt(db: AsyncSession, story_access_id: int):
    attempt = await get_last_instance(
        db, Attempt, order_by="id", story_access_id=story_access_id
    )
    if attempt:
        return attempt
    return None


async def get_hints(attempt_id: int, db: AsyncSession):
    return await get_instances(db, HintsAttempt, attempt_id=attempt_id)
