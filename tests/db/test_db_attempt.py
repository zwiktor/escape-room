import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import *
from db.db_attempt import *
from db.db_queries import get_instance, get_or_create, get_last_instance
from schemas.attempt import AttemptDisplay
from schemas.stage import StageDisplay


@pytest.mark.asyncio
async def test_get_attempt_valid_data(session: AsyncSession, mock_user: User):
    """
    Test case for a valid attempt using data from test_data.json.
    Expected: Data matches the AttemptDisplay schema.
    """
    # Wybieramy attempt_id zgodne z test_data.json
    attempt_id = 1  # Attempt dla użytkownika user1@example.com
    result = await get_attempt(attempt_id=attempt_id, db=session)

    # Sprawdzenie danych
    assert result is not None
    assert isinstance(result, dict)
    assert "start_date" in result
    assert "stage" in result

    # Sprawdzenie zgodności z AttemptDisplay
    attempt_display = AttemptDisplay(**result)
    assert attempt_display.start_date is not None
    assert isinstance(attempt_display.stage, StageDisplay)
    assert isinstance(attempt_display.stage.name, str)
    assert isinstance(attempt_display.stage.level, int)
    assert isinstance(attempt_display.stage.question, str)
    assert attempt_display.stage.level == 1
    assert attempt_display.stage.name == "First Challenge"


@pytest.mark.asyncio
async def test_get_attempt_invalid_id(session: AsyncSession, mock_user: User):
    """
    Test case for an invalid attempt ID.
    Expected: None or an exception is raised.
    """
    invalid_attempt_id = 999  # Nieistniejący attempt_id
    with pytest.raises(Exception):  # Oczekiwanie odpowiedniego wyjątku
        await get_attempt(attempt_id=invalid_attempt_id, db=session)
