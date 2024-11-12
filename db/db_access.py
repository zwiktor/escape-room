from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import Story, Stage, StoryAccess, Attempt

from db.db_queries import get_instance, get_or_create, get_last_instance
from db.models import User


async def check_status(db: AsyncSession, user: User, story_id: int):
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
