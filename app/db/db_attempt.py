from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Attempt,
    HintsAttempt,
    Hint,
    Stage,
    StoryAccess,
    PasswordAttempt,
)
from app.db.db_queries import (
    get_instance,
    get_instances,
    get_last_instance,
    get_first_instance,
    create_instance,
)
from datetime import datetime


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
    first_stage = await get_first_instance(
        db, Stage, order_by="id", story_id=story_access.story_id
    )
    if not first_stage:
        raise ValueError("There is no stage for the Story")

    try:
        new_attempt = Attempt(
            story_access_id=story_access.id,
            stage_id=first_stage.id,
        )
        db.add(new_attempt)
        await db.commit()
        await db.refresh(new_attempt)
        return new_attempt
    except Exception as e:
        await db.rollback()
        raise Exception(f"Failed to create the first attempt: {str(e)}")


async def add_password_attempt(session: AsyncSession, attempt: Attempt, password: str):
    return await create_instance(
        session, PasswordAttempt, attempt_id=attempt.id, password=password
    )


async def check_new_hint(session: AsyncSession, attempt: Attempt, password: str):
    hint = await get_instance(
        session, Hint, stage_id=attempt.stage_id, trigger=password
    )
    if hint:
        if not await get_instance(
            session, HintsAttempt, attempt_id=attempt.id, hint_id=hint.id
        ):
            await create_instance(
                session,
                HintsAttempt,
                attempt_id=attempt.id,
                hint_id=hint.id,
                enter_date=datetime.now(),
            )
            return True

    return False


async def finish_attempt(session: AsyncSession, attempt: Attempt):
    attempt.finish_date = datetime.now()
    await session.commit()
    return attempt


async def create_next_attempt(
    session: AsyncSession, attempt: Attempt, next_stage: Stage
):
    return await create_instance(
        session,
        Attempt,
        story_access_id=attempt.story_access_id,
        stage_id=next_stage.id,
        start_date=attempt.finish_date,
    )
