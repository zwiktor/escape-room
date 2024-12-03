from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt
from typing import Optional
from uuid import UUID

from db.db_queries import get_instance, get_or_create, get_last_instance
from db.models import User


async def get_story_access(db: AsyncSession, user: User, story_id: int) -> StoryAccess:
    """Fetch a specific StoryAccess instance."""
    return await get_instance(db, StoryAccess, user_id=user.id, story_id=story_id)


async def get_story_access_by_attempt(
    db: AsyncSession, attempt_id: int, user: User
) -> Optional[StoryAccess]:
    """Fetch a specific StoryAccess instance by attempt."""
    attempt = await get_instance(db, Attempt, id=attempt_id)
    if attempt:
        await db.refresh(attempt, ["access"])
        story_access = attempt.access
        if story_access.user_id == user.id:
            await db.refresh(story_access, ["story"])
            return story_access
    return None
