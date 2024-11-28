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


async def get_attempt_by_id_with_user(db: AsyncSession, attempt_id: int, user: User):
    attempt = await get_instance(db, Attempt, id=attempt_id)
    if attempt:
        return attempt
    return None


async def get_hints(attempt_id: int, db: AsyncSession, user: User):
    hints_attempts = await get_instances(db, HintsAttempt, attempt_id=attempt_id)
    hints_id = [hints_attempt.hint_id for hints_attempt in hints_attempts]
    hints = await get_instances(db, Hint, id=hints_id)
    return convert_to_pydantic(hints, HintBase)


async def add_hint_to_attempt(attempt_id: int, db: AsyncSession, hint: int):
    hint = await get_or_create(
        db, HintsAttempt, attempt_id=attempt_id, hint_id=hint, enter_date=datetime.now()
    )
    return None


async def add_password_attempt(attempt_id: int, db: AsyncSession, password: str):
    await create_instance(
        db,
        PasswordAttempt,
        attempt_id=attempt_id,
        password=password,
        enter_date=datetime.now(),
    )


async def finish_attempt(attempt: Attempt, db: AsyncSession):
    attempt.finish_date = datetime.now()
    await db.commit()
    await db.refresh(attempt)
    return attempt


async def progress_story(stage: Stage, attempt: Attempt, db: AsyncSession):
    new_attempt, is_story_finished = None, False
    attempt = await finish_attempt(attempt, db)
    next_stage = await get_next_stage(stage, db)
    if next_stage:
        new_attempt = await get_or_create(
            db,
            Attempt,
            story_access_id=attempt.story_access_id,
            stage_id=next_stage.id,
            start_date=attempt.finish_date,
        )
    else:
        is_story_finished = True
    return new_attempt, is_story_finished


async def check_stage_password(
    stage: Stage, attempt: Attempt, db: AsyncSession, password: str
):
    if stage.password == password:
        return await progress_story(stage, attempt, db)
    return None, False


async def check_hint_password(
    stage: Stage, attempt: Attempt, db: AsyncSession, password: str
):
    hint = await get_instance(db, Hint, stage_id=stage.id, trigger=password)
    if hint:
        attempt_hint = await get_instance(
            db, HintsAttempt, attempt_id=attempt.id, hint_id=hint.id
        )
        if not attempt_hint:
            await add_hint_to_attempt(attempt.id, db, hint.id)
            return True, "Nowa wskazowka zostala odkryta"
        else:
            return False, "Ta wskazowka zostala juz odkryta"

    return False, "Nieprawidlowe haslo"


async def validate_password(
    request: PasswordFormBase, attempt_id: int, db: AsyncSession, user: User
):
    data = {
        "message": "Ten etap zostal juz rozwiazany",
        "new_hint": False,
        "end_story": False,
    }
    await add_password_attempt(attempt_id, db, request.password)
    attempt = await get_instance(db, Attempt, id=attempt_id)
    stage = await get_instance(db, Stage, id=attempt.stage_id)

    if attempt.finish_date:
        return data

    new_attempt, is_story_finished = await check_stage_password(
        stage, attempt, db, request.password
    )
    if_new_hint, message = await check_hint_password(
        stage, attempt, db, request.password
    )
    data["message"] = message
    data["new_hint"] = if_new_hint

    if new_attempt:
        data["message"] = "Gratulacje, to prawidlowa odpowiedz"
        data["next_attempt"] = new_attempt.id
    elif is_story_finished:
        data["message"] = "Gratulacje, historia zostala zakonczona"
        data["end_story"] = True

    return data
