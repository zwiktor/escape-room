import pytest
from pydantic import ValidationError
from datetime import datetime
from schemas.story import StoryDisplay, StoryBase  # Adjust to the correct import path


def test_story_base_schema():
    # Valid data with all fields included
    valid_data = {
        "id": 1,
        "title": "Mystery Adventure",
        "description": "A thrilling mystery story.",
        "type": "Adventure",
        "difficulty": "Medium",
        "rating": 4.5,
        "cost": 20,
        "create_date": datetime(2023, 1, 1, 12, 0, 0),
    }

    try:
        # Attempt to create StoryBase instance
        story_base = StoryBase(**valid_data)
        assert story_base.id == 1
        assert story_base.title == "Mystery Adventure"
        assert story_base.description == "A thrilling mystery story."
        assert story_base.type == "Adventure"
        assert story_base.difficulty == "Medium"
        assert story_base.rating == 4.5
        assert story_base.cost == 20
        assert story_base.create_date == datetime(2023, 1, 1, 12, 0, 0)
    except ValidationError as e:
        # Print the error details for debugging
        print("Validation Error for valid_data:", e.errors())
        raise

    # Valid data without optional create_date
    minimal_data = {
        "id": 2,
        "title": "Mystery Adventure",
        "description": "A thrilling mystery story.",
        "type": "Adventure",
        "difficulty": "Medium",
        "cost": 20,
    }

    try:
        story_base = StoryBase(**minimal_data)
        assert story_base.create_date is None  # create_date should default to None
    except ValidationError as e:
        print("Validation Error for minimal_data:", e.errors())
        raise

    # Invalid data: wrong data type for create_date
    with pytest.raises(ValidationError) as exc_info:
        StoryBase(
            id=1,
            title="Mystery Adventure",
            description="A thrilling mystery story.",
            type="Adventure",
            difficulty="Medium",
            rating=4.5,
            cost=20,
            create_date="not_a_datetime",
        )

    # Check for specific error details in the exception
    assert "create_date" in str(exc_info.value)
    assert "Input should be a valid datetime" in str(exc_info.value)
