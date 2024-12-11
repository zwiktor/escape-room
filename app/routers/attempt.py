from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
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
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    attempt_display = await db_attempt.get_attempt(db, attempt_id, user)
    return attempt_display


@router.post("/{attempt_id}/hints", response_model=HintsDisplay)
async def get_hints(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    hints_list = await db_attempt.get_hints(attempt_id, db, user)
    return HintsDisplay(hints=hints_list)


@router.post("/{attempt_id}/check_password", response_model=PasswordCheckDisplay)
async def password_validation(
    request: PasswordFormBase,
    attempt_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    attempt_response = await db_attempt.validate_password(request, attempt_id, db, user)
    return attempt_response
