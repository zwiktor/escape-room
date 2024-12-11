import pytest
from httpx import AsyncClient
from tests.routers.test_login import login_and_get_token


@pytest.mark.asyncio
async def test_get_attempt_valid_authorization(async_client: AsyncClient):
    """
    Test that the endpoint returns the attempt details when the user is logged in
    and has access to the specified attempt ID.
    """
    token = await login_and_get_token(async_client)

    # Access the story endpoint
    response = await async_client.post(
        "/attempt/2", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["start_date"] is not None
    assert data["stage"]["name"] == "Second Challenge"
    assert data["stage"]["level"] == 2
    assert data["stage"]["question"] == "What is your quest?"


@pytest.mark.asyncio
async def test_get_attempt_unauthorized_access():
    """
    Test that the endpoint returns a 401 Unauthorized error when no valid token
    is provided.
    """


@pytest.mark.asyncio
async def test_get_attempt_invalid_attempt_id():
    """
    Test that the endpoint returns a 404 Not Found error when the provided attempt ID
    does not exist in the database.
    """


@pytest.mark.asyncio
async def test_get_attempt_no_access_to_attempt():
    """
    Test that the endpoint returns a 403 Forbidden error when the logged-in user
    does not have access to the specified attempt ID.
    """


@pytest.mark.asyncio
async def test_get_attempt_correct_response_model():
    """
    Test that the response data matches the `AttemptDisplay` response model
    for a valid request.
    """


@pytest.mark.asyncio
async def test_get_attempt_for_completed_attempt():
    """
    Test that the endpoint correctly returns details for a completed attempt
    (with a `finish_date` set).
    """


@pytest.mark.asyncio
async def test_get_attempt_for_in_progress_attempt():
    """
    Test that the endpoint correctly returns details for an in-progress attempt
    (without a `finish_date` set).
    """


@pytest.mark.asyncio
async def test_get_attempt_for_invalid_token():
    """
    Test that the endpoint returns a 401 Unauthorized error when an invalid token
    is used in the Authorization header.
    """


@pytest.mark.asyncio
async def test_get_attempt_for_different_user_attempt():
    """
    Test that the endpoint returns a 403 Forbidden error when the logged-in user
    tries to access an attempt belonging to a different user.
    """


@pytest.mark.asyncio
async def test_get_attempt_with_missing_attempt_id():
    """
    Test that the endpoint returns a 422 Unprocessable Entity error when no
    attempt ID is provided in the request.
    """
