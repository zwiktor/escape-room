import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import uuid4
from app.schemas.access import (
    StatusEnum,
    AttemptBase,
    AccessBase,
    StoryAccessBase,
    StoryStatus,
)

# your actual import path

# Fixture data for testing
valid_uuid = uuid4()
current_time = datetime.now()


# Test for StatusEnum
def test_status_enum():
    # Check that valid enum values are accepted
    assert StatusEnum.new == "new"
    assert StatusEnum.purchased == "purchased"
    assert StatusEnum.started == "started"
    assert StatusEnum.ended == "finished"

    # Check that invalid enum values raise an error
    with pytest.raises(ValueError):
        StatusEnum("invalid_status")


# Test for AttemptBase schema
def test_attempt_base_schema():
    # Valid data
    valid_data = {
        "id": 1,
        "story_access_id": 10,
        "stage_id": 5,
        "start_date": current_time,
        "finish_date": current_time,
    }
    attempt = AttemptBase(**valid_data)
    assert attempt.id == 1
    assert attempt.story_access_id == 10
    assert attempt.stage_id == 5
    assert attempt.start_date == current_time
    assert attempt.finish_date == current_time

    # Invalid data: missing required fields
    with pytest.raises(ValidationError):
        AttemptBase(story_access_id=10, stage_id=5, start_date=current_time)

    # Invalid data: wrong data type
    with pytest.raises(ValidationError):
        AttemptBase(
            id="wrong_type",
            story_access_id="wrong_type",
            stage_id="wrong_type",
            start_date="wrong_type",
        )


# Test for AccessBase schema
def test_access_base_schema():
    # Valid data
    valid_data = {
        "id": 2,
        "user_id": valid_uuid,
        "story_id": 20,
        "purchase_date": current_time,
    }
    access = AccessBase(**valid_data)
    assert access.id == 2
    assert access.user_id == valid_uuid
    assert access.story_id == 20
    assert access.purchase_date == current_time

    # Invalid data: missing required fields
    with pytest.raises(ValidationError):
        AccessBase(id=2, story_id=20, purchase_date=current_time)

    # Invalid data: wrong data type
    with pytest.raises(ValidationError):
        AccessBase(id=2, user_id="not_a_uuid", story_id=20, purchase_date=current_time)


# Test for StoryAccessBase schema
def test_story_access_base_schema():
    # Valid data with nested AttemptBase
    valid_data = {
        "purchase_date": current_time,
        "current_attempt": {
            "id": 1,
            "story_access_id": 10,
            "stage_id": 5,
            "start_date": current_time,
            "finish_date": current_time,
        },
    }
    story_access = StoryAccessBase(**valid_data)
    assert story_access.purchase_date == current_time
    assert story_access.current_attempt.id == 1
    assert story_access.current_attempt.story_access_id == 10

    # Invalid data: wrong type for nested field
    with pytest.raises(ValidationError):
        StoryAccessBase(
            purchase_date=current_time, current_attempt="not_an_attempt_instance"
        )


# Test for StoryStatus schema
def test_story_status_schema():
    # Valid data with nested StoryAccessBase
    valid_data = {
        "status": "new",
        "story_access": {
            "purchase_date": current_time,
            "current_attempt": {
                "id": 1,
                "story_access_id": 10,
                "stage_id": 5,
                "start_date": current_time,
                "finish_date": current_time,
            },
        },
    }
    story_status = StoryStatus(**valid_data)
    assert story_status.status == StatusEnum.new
    assert story_status.story_access.purchase_date == current_time
    assert story_status.story_access.current_attempt.id == 1

    # Invalid data: wrong enum value
    with pytest.raises(ValidationError):
        StoryStatus(status="invalid_status", story_access=valid_data["story_access"])

    # Invalid data: wrong type for nested StoryAccessBase
    with pytest.raises(ValidationError):
        StoryStatus(status="new", story_access="not_a_story_access_instance")
