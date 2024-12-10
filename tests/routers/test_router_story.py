import pytest
from httpx import AsyncClient
from sqlalchemy import text


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


@pytest.mark.asyncio
async def test_get_all_stories_empty(async_client: AsyncClient, session):
    """
    Test retrieving all stories when no stories exist in the database.
    """
    # Remove all stories from the database
    await session.execute(text("DELETE FROM story"))
    await session.commit()

    response = await async_client.get("/story/")
    assert response.status_code == 200, "Expected status code to be 200"
    data = response.json()
    assert isinstance(data, list), "Response should be a list."
    assert len(data) == 0, "The list of stories should be empty."


@pytest.mark.asyncio
async def test_get_all_stories_cors(async_client: AsyncClient):
    """
    Test CORS headers in the response.
    """
    headers = {"Origin": "http://localhost:3000"}
    response = await async_client.get("/story/", headers=headers)
    assert response.status_code == 200, "Expected status code to be 200"
    assert (
        "access-control-allow-origin" in response.headers
    ), "CORS headers should be present in the response."
    assert (
        response.headers["access-control-allow-origin"] == "http://localhost:3000"
    ), "CORS origin should match the frontend origin."
