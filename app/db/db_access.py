from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StoryAccess, Attempt
from typing import Optional

from app.db.db_queries import get_instance
from app.db.models import User
from app.exceptions.exceptions import EntityDoesNotExistError, UnAuthenticatedUserError


async def get_story_access(db: AsyncSession, user: User, story_id: int) -> StoryAccess:
    """Fetch a specific StoryAccess instance."""
    return await get_instance(db, StoryAccess, user_id=user.id, story_id=story_id)


async def get_story_access_by_attempt(
    db: AsyncSession, attempt_id: int, user: User
) -> Optional[StoryAccess]:
    """Fetch a specific StoryAccess instance by attempt."""
    attempt = await get_instance(db, Attempt, id=attempt_id)
    if not attempt:
        raise EntityDoesNotExistError(
            message=f"Attempt with {attempt_id} id does not exist"
        )
    await db.refresh(attempt, ["access"])
    story_access = attempt.access
    if story_access.user_id == user.id:
        await db.refresh(story_access, ["story"])
        return story_access
    else:
        raise UnAuthenticatedUserError(
            message="User doesn't have access to this attempt"
        )
