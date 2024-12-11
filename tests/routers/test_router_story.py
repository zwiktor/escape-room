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
    Test if response will be 404 for invalid story ID
    """
    token = await login_and_get_token(async_client)
    response = await async_client.post(
        "/story/999/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Story with id {999} not found. [EscapeRoom]"


@pytest.mark.asyncio
async def test_buy_story_already_bought(async_client: AsyncClient):
    """
    Test if story hass been bought earlier -> properly response
    """
    token = await login_and_get_token(async_client)
    response = await async_client.post(
        "/story/1/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == f"User already owns this story. [EscapeRoom]"


@pytest.mark.asyncio
async def test_start_story_authorization_failed(async_client: AsyncClient):
    """
    Test if starting a story requires authorization.
    """
    response = await async_client.post("/story/1/start/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_story_valid_process(async_client: AsyncClient):
    """
    Test if starting story working properly
    """

    # Log in to authenticate
    token = await login_and_get_token(async_client, "user4", "hashed4")

    # Buy the story
    response = await async_client.post(
        "/story/1/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Start the story
    response = await async_client.post(
        "/story/1/start/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"


@pytest.mark.asyncio
async def test_start_story_unvalid_story_id(async_client: AsyncClient):
    """
    Test if response will be 404 for invalid story ID
    """
    token = await login_and_get_token(async_client)
    response = await async_client.post(
        "/story/999/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Story with id {999} not found. [EscapeRoom]"


@pytest.mark.asyncio
async def test_start_story_already_started(async_client: AsyncClient):
    """
    Test if starting story return valid resopnse with 400 status code and message
    """
    # Log in to authenticate
    token = await login_and_get_token(async_client)

    # Start the story
    response = await async_client.post(
        "/story/1/start/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User has already started this story [EscapeRoom]"


@pytest.mark.asyncio
async def test_check_access_for_new_story(async_client: AsyncClient):
    """
    Test story_acces in initial state
    """
    # Log in to authenticate
    token = await login_and_get_token(async_client, "user4", "hashed4")

    # check access
    response = await async_client.post(
        "/story/1/access/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "new"
    assert data["story_access"] is None


@pytest.mark.asyncio
async def test_check_access_purchased(async_client: AsyncClient):
    """
    Test story_acces for purchased state
    """
    token = await login_and_get_token(async_client, "user4", "hashed4")

    # Buy the story
    response = await async_client.post(
        "/story/1/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # check access
    response = await async_client.post(
        "/story/1/access/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "purchased"
    assert data["story_access"]["purchase_date"] is not None
    assert data["story_access"]["current_attempt"] is None


@pytest.mark.asyncio
async def test_check_access_started(async_client: AsyncClient):
    """
    Test story_acces for started state, check attempt id and stage
    """
    token = await login_and_get_token(async_client, "user4", "hashed4")

    # Buy the story
    response = await async_client.post(
        "/story/1/buy/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # Start the story
    response = await async_client.post(
        "/story/1/start/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # check access
    response = await async_client.post(
        "/story/1/access/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "started"
    assert data["story_access"]["purchase_date"] is not None
    assert data["story_access"]["current_attempt"] is not None


@pytest.mark.asyncio
async def test_check_access_ended(async_client: AsyncClient):
    """
    Test story_acces for finished story with finish_date set
    """
    token = await login_and_get_token(async_client)

    # check access
    response = await async_client.post(
        "/story/4/access/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "finished"
    assert data["story_access"]["purchase_date"] is not None
    assert data["story_access"]["current_attempt"] is not None
    assert data["story_access"]["current_attempt"]["finish_date"] is not None
    assert (
        data["story_access"]["purchase_date"]
        < data["story_access"]["current_attempt"]["finish_date"]
    )
