import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_stories_valid(async_client: AsyncClient, session):
    """
    Test retrieving all stories when stories exist in the database.
    """
    # Ensure test data is populated by the setup_database fixture
    response = await async_client.get("/story/")
    assert response.status_code == 200, "Expected status code to be 200"
    data = response.json()
    assert isinstance(data, list), "Response should be a list."
    assert len(data) > 0, "There should be at least one story."
    assert all(
        "title" in story and "cost" in story for story in data
    ), "Each story should contain 'title' and 'cost'."
    assert data[0].get("title") == "Adventure Story"
