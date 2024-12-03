from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Attempt, HintsAttempt, Hint, Stage, StoryAccess
from db.db_queries import (
    get_instance,
    get_instances,
    get_last_instance,
    get_first_instance,
)


async def get_active_attempt(db: AsyncSession, story_access_id: int):
    attempt = await get_last_instance(
        db, Attempt, order_by="id", story_access_id=story_access_id
    )
    if attempt:
        return attempt
    return None


async def get_hints(db: AsyncSession, attempt_id: int):
    hints_attempts = await get_instances(db, HintsAttempt, attempt_id=attempt_id)
    hints_id = [hints_attempt.hint_id for hints_attempt in hints_attempts]
    return await get_instances(db, Hint, id=hints_id)


async def create_first_attempt(db: AsyncSession, story_access: StoryAccess) -> Attempt:
    """
    Creates the first attempt for a story.

    :param db: Database session.
    :param story_access: story_access object
    :return: The newly created Attempt.
    :raises Exception: If the attempt creation fails.
    """
    first_stage_id = get_first_instance(
        db, Stage, order_by="id", story_id=story_access.story_id
    )
    try:
        new_attempt = Attempt(
            story_access_id=story_access.id,
            stage_id=first_stage_id,
        )
        db.add(new_attempt)
        await db.commit()
        await db.refresh(new_attempt)
        return new_attempt
    except Exception as e:
        await db.rollback()
        raise Exception(f"Failed to create the first attempt: {str(e)}")
