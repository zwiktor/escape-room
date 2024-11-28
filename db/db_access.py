from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt
from typing import Optional
from uuid import UUID

from db.db_queries import get_instance, get_or_create, get_last_instance
from db.models import User


async def get_story_access(db: AsyncSession, user: User, story_id: int) -> StoryAccess:
    """Fetch a specific StoryAccess instance."""
    return await get_instance(db, StoryAccess, user_id=user_id, story_id=story_id)


async def get_story_access_by_attempt(
    db: AsyncSession, attempt_id: int, user: User
) -> Optional[StoryAccess]:
    """Fetch a specific StoryAccess instance by attempt."""
    attempt = await get_instance(db, Attempt, id=attempt_id)
    story_access = attempt.access
    if story_access.user_id == user.id:
        return await get_instance(db, StoryAccess, user_id=user_id, story_id=story_id)
    return None


async def check_status(db: AsyncSession, user: User, story_id: int):
    story = await get_instance(db, Story, id=story_id)
    if not story:
        return None

    data = {
        "status": "new",
        "story_access": {"purchase_date": None, "current_attempt": None},
    }
    attempt = None
    story_access = await get_instance(
        session=db, model=StoryAccess, story_id=story_id, user_id=user.id
    )
    if story_access:
        attempt = await get_last_instance(
            session=db,
            model=Attempt,
            order_by=Attempt.start_date,
            story_access_id=story_access.id,
        )

        data["status"] = "purchased"
        data["story_access"]["purchase_date"] = story_access.purchase_date

    if attempt:
        data["status"] = "started"
        data["story_access"]["current_attempt"] = attempt

        if attempt.finish_date:
            data["status"] = "finished"

    return data
