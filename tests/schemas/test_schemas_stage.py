import pytest
from pydantic import ValidationError
from schemas.stage import (
    StageDisplay,
    StageBase,
)  # Replace with the correct path to your models


# Test for StageDisplay schema
def test_stage_display_schema():
    # Valid data
    valid_data = {
        "name": "Stage 1",
        "level": 1,
        "question": "What is the answer to life?",
    }
    stage_display = StageDisplay(**valid_data)
    assert stage_display.name == "Stage 1"
    assert stage_display.level == 1
    assert stage_display.question == "What is the answer to life?"

    # Invalid data: missing required fields
    with pytest.raises(ValidationError) as exc_info:
        StageDisplay(level=1, question="What is the answer to life?")
    assert "name" in str(exc_info.value)

    # Invalid data: wrong data type for level
    with pytest.raises(ValidationError) as exc_info:
        StageDisplay(
            name="Stage 1", level="not_an_int", question="What is the answer to life?"
        )
    # Adjusted assertion to match updated Pydantic error message format
    assert "Input should be a valid integer" in str(
        exc_info.value
    ) or "unable to parse string as an integer" in str(exc_info.value)


# Test for StageBase schema
def test_stage_base_schema():
    # Valid data
    valid_data = {
        "name": "Stage 1",
        "level": 1,
        "question": "What is the answer to life?",
        "password": "secure_password",
        "story_id": 100,
    }
    stage_base = StageBase(**valid_data)
    assert stage_base.name == "Stage 1"
    assert stage_base.level == 1
    assert stage_base.question == "What is the answer to life?"
    assert stage_base.password == "secure_password"
    assert stage_base.story_id == 100

    # Invalid data: missing required fields
    with pytest.raises(ValidationError) as exc_info:
        StageBase(
            name="Stage 1",
            level=1,
            question="What is the answer to life?",
            password="secure_password",
        )
    assert "story_id" in str(exc_info.value)

    # Invalid data: wrong data type for password
    with pytest.raises(ValidationError) as exc_info:
        StageBase(
            name="Stage 1",
            level=1,
            question="What is the answer to life?",
            password=12345,
            story_id=100,
        )
    # Adjusted assertion for string validation error
    assert "Input should be a valid string" in str(
        exc_info.value
    ) or "type=string_type" in str(exc_info.value)
