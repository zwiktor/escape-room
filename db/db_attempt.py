from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.models import (
    User,
    Attempt,
    Stage,
    Hint,
    HintsAttempt,
    PasswordAttempt,
    StoryAccess,
)
from db.db_stage import get_next_stage
from db.db_queries import (
    get_instance,
    get_instances,
    get_or_create,
    get_last_instance,
    convert_to_pydantic,
    create_instance,
)
from schemas.attempt import (
    AttemptDisplay,
    HintBase,
    PasswordFormBase,
    PasswordCheckDisplay,
)
from schemas.stage import StageDisplay

from sqlalchemy import func


async def get_active_attempt(db: AsyncSession, story_access_id: int):
    attempt = await get_last_instance(
        db, Attempt, order_by="id", story_access_id=story_access_id
    )
    if attempt:
        return attempt
    return None


async def get_hints(attempt_id: int, db: AsyncSession, user: User):
    hints_attempts = await get_instances(db, HintsAttempt, attempt_id=attempt_id)
    hints_id = [hints_attempt.hint_id for hints_attempt in hints_attempts]
    hints = await get_instances(db, Hint, id=hints_id)
    return convert_to_pydantic(hints, HintBase)
