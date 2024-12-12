import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.attempt import (
    HintBase,
    HintsDisplay,
    AttemptDisplay,
    PasswordFormBase,
    PasswordCheckDisplay,
)  # Adjust import paths as necessary

# Fixture data for testing
current_time = datetime.now()


# Test for HintBase schema
def test_hint_base_schema():
    # Valid data
    valid_data = {"text": "This is a hint.", "trigger": "hint_trigger"}
    hint = HintBase(**valid_data)
    assert hint.text == "This is a hint."
    assert hint.trigger == "hint_trigger"

    # Invalid data: missing required fields
    with pytest.raises(ValidationError):
        HintBase(text="This is a hint.")

    # Invalid data: wrong data type
    with pytest.raises(ValidationError):
        HintBase(text="This is a hint.", trigger=123)  # `trigger` should be a string


# Test for HintsDisplay schema
def test_hints_display_schema():
    # Valid data with a list of HintBase
    valid_data = {
        "hints": [
            {"text": "Hint 1", "trigger": "trigger1"},
            {"text": "Hint 2", "trigger": "trigger2"},
        ]
    }
    hints_display = HintsDisplay(**valid_data)
    assert len(hints_display.hints) == 2
    assert hints_display.hints[0].text == "Hint 1"
    assert hints_display.hints[1].trigger == "trigger2"

    # Invalid data: wrong type for hints
    with pytest.raises(ValidationError):
        HintsDisplay(hints="not_a_list")


# Test for AttemptDisplay schema
def test_attempt_display_schema():
    # Valid data with nested StageDisplay
    stage_data = {"name": "Stage 1", "level": 1, "question": "This is a test stage"}
    valid_data = {"start_date": current_time, "stage": stage_data, "is_finished": False}
    attempt_display = AttemptDisplay(**valid_data)
    assert attempt_display.start_date == current_time
    assert attempt_display.stage.name == "Stage 1"

    # Invalid data: missing required fields
    with pytest.raises(ValidationError):
        AttemptDisplay(start_date=current_time)

    # Invalid data: wrong type for nested field
    with pytest.raises(ValidationError):
        AttemptDisplay(start_date=current_time, stage="not_a_stage")


# Test for PasswordFormBase schema
def test_password_form_base_schema():
    # Valid data
    valid_data = {"password": "securepassword"}
    password_form = PasswordFormBase(**valid_data)
    assert password_form.password == "securepassword"

    # Invalid data: missing password field
    with pytest.raises(ValidationError):
        PasswordFormBase()

    # Invalid data: wrong data type for password
    with pytest.raises(ValidationError):
        PasswordFormBase(password=12345)  # `password` should be a string


# Test for PasswordCheckDisplay schema
def test_password_check_display_schema():
    # Valid data with all fields specified
    valid_data = {
        "message": "Password correct.",
        "new_hint": True,
        "next_attempt": 3,
        "end_story": True,
    }
    password_check = PasswordCheckDisplay(**valid_data)
    assert password_check.message == "Password correct."
    assert password_check.new_hint is True
    assert password_check.next_attempt == 3
    assert password_check.end_story is True

    # Valid data with only required field
    minimal_data = {"message": "Try again."}
    password_check = PasswordCheckDisplay(**minimal_data)
    assert password_check.message == "Try again."
    assert password_check.new_hint is False  # Default value
    assert password_check.next_attempt is None  # Default value
    assert password_check.end_story is False  # Default value

    # Invalid data: wrong type for next_attempt
    with pytest.raises(ValidationError):
        PasswordCheckDisplay(message="Password correct.", next_attempt="not_an_int")
