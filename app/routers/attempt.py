from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.storymanager import StoryManager, get_story_manager
from app.schemas.attempt import (
    AttemptDisplay,
    HintsDisplay,
    PasswordCheckDisplay,
    PasswordFormBase,
)

from app.db import db_attempt
from app.db.models import User

from app.users.manager import current_active_user

router = APIRouter(prefix="/attempt", tags=["attempt"])


@router.post("/{attempt_id}", response_model=AttemptDisplay)
async def get_attempt(
    attempt_id: int,
    story_manager: StoryManager = Depends(get_story_manager),
):
    await story_manager.load_by_attempt_id(attempt_id)

    attempt = await story_manager.get_attempt()
    return attempt


@router.post("/{attempt_id}/hints", response_model=HintsDisplay)
async def get_hints(
    attempt_id: int,
    story_manager: StoryManager = Depends(get_story_manager),
):
    await story_manager.load_by_attempt_id(attempt_id)
    hints_list = await story_manager.get_hints()
    return hints_list


@router.post("/{attempt_id}/check_password", response_model=PasswordCheckDisplay)
async def password_validation(
    request: PasswordFormBase,
    attempt_id: int,
    story_manager: StoryManager = Depends(get_story_manager),
):
    await story_manager.load_by_attempt_id(attempt_id)
    check_password = await story_manager.validate_password(request.password)
    return check_password
