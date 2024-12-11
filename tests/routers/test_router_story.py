import pytest
from httpx import AsyncClient
from sqlalchemy import text
from tests.routers.test_login import login_and_get_token


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


@pytest.mark.asyncio
async def test_get_story_valid_authorization(async_client: AsyncClient):
    """
    Test retrieving story details with valid authorization.
    """
    token = await login_and_get_token(async_client)

    # Access the story endpoint
    response = await async_client.post(
        "/story/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Adventure Story"
    response = await async_client.post(
        "/story/1", headers={"Authorization": f"Bearer {token}"}
    )


@pytest.mark.asyncio
async def test_get_story_unauthorized(async_client: AsyncClient):
    """
    Test retrieving story details without authorization.
    """
    response = await async_client.post("/story/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_story_check_response_model(async_client: AsyncClient):
    """
    Test response model for /story/{story_id} endpoint.
    """
    token = await login_and_get_token(async_client)
    response = await async_client.post(
        "/story/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data and "title" in data and "cost" in data


@pytest.mark.asyncio
async def test_buy_story_unauthorized(async_client: AsyncClient):
    """
    Test authentication for buy_sotry
    """
    response = await async_client.post("/story/1/buy/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_buy_story_success_boutght(async_client: AsyncClient):
    """
    Test succesfull scenario
    """
    token = await login_and_get_token(async_client, "user4", "hashed4")
    response = await async_client.post(
        "/story/1/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "purchased"


@pytest.mark.asyncio
async def test_buy_story_unvalid_story_id(async_client: AsyncClient):
    """
    Test if response will be bad_request
    """
    pass


@pytest.mark.asyncio
async def test_buy_story_already_bought(async_client: AsyncClient):
    """
    Test if story hass been bought earlier -> properly response
    """
    pass


@pytest.mark.asyncio
async def test_start_story_authorization(async_client: AsyncClient):
    """
    Test if starting story need authorization
    """
    pass


@pytest.mark.asyncio
async def test_start_story_valid_process(async_client: AsyncClient):
    """
    Test if starting story working properly
    """
    pass


@pytest.mark.asyncio
async def test_start_story_unvalid_story_id(async_client: AsyncClient):
    """
    Test if starting story return valid resopnse with 400 status code and message
    """
    pass


@pytest.mark.asyncio
async def test_start_story_already_started(async_client: AsyncClient):
    """
    Test if starting story return valid resopnse with 400 status code and message
    """
    pass


@pytest.mark.asyncio
async def test_check_access_for_new_story(async_client: AsyncClient):
    """
    Test story_acces in initial state
    """
    pass


@pytest.mark.asyncio
async def test_check_access_purchased(async_client: AsyncClient):
    """
    Test story_acces for purchased state
    """
    pass


@pytest.mark.asyncio
async def test_check_access_started(async_client: AsyncClient):
    """
    Test story_acces for started state, check attempt id and stage
    """
    pass


@pytest.mark.asyncio
async def test_check_access_ended(async_client: AsyncClient):
    """
    Test story_acces for finished story with finish_date set
    """
    pass
