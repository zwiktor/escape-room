import pytest
from httpx import AsyncClient
from tests.routers.test_login import login_and_get_token


@pytest.mark.asyncio
async def test_get_attempt_valid_authorization(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns the attempt details when the user is logged in
    and has access to the specified attempt ID.
    """

    # Access the story endpoint
    response = await async_client.post("/attempt/2", headers=authorized_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["start_date"] is not None
    assert data["stage"]["name"] == "Second Challenge"
    assert data["stage"]["level"] == 2
    assert data["stage"]["question"] == "What is your quest?"


@pytest.mark.asyncio
async def test_get_attempt_unauthorized_access(async_client: AsyncClient):
    """
    Test that the endpoint returns a 401 Unauthorized error when no valid token
    is provided.
    """
    response = await async_client.post("/attempt/2")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_get_attempt_invalid_attempt_id(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns a 404 Not Found error when the provided attempt ID
    does not exist in the database.
    """
    response = await async_client.post("/attempt/999", headers=authorized_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Attempt with {999} id does not exist [EscapeRoom]"


@pytest.mark.asyncio
async def test_get_attempt_no_access_to_attempt(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns a 403 Forbidden error when the logged-in user
    does not have access to the specified attempt ID.
    """
    response = await async_client.post("/attempt/5", headers=authorized_headers)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == f"User doesn't have access to this attempt [EscapeRoom]"


@pytest.mark.asyncio
async def test_get_attempt_for_completed_attempt(async_client: AsyncClient):
    """
    Test that the endpoint correctly returns details for a completed attempt
    (with a `finish_date` set).
    """
    token = await login_and_get_token(async_client)
    response = await async_client.post(
        "/attempt/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["stage"] is not None
    assert data["is_finished"] is True


@pytest.mark.asyncio
async def test_get_attempt_for_in_progress_attempt(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint correctly returns details for an in-progress attempt
    (without a `finish_date` set).
    """
    response = await async_client.post("/attempt/2", headers=authorized_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["stage"] is not None
    assert data["is_finished"] is False


@pytest.mark.asyncio
async def test_get_attempt_for_invalid_token(async_client: AsyncClient):
    """
    Test that the endpoint returns a 401 Unauthorized error when an invalid token
    is used in the Authorization header.
    """
    token = "asdasdasdasda"
    response = await async_client.post(
        "/attempt/2", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_get_attempt_with_missing_attempt_id(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns a 422 Unprocessable Entity error when no
    attempt ID is provided in the request.
    """
    response = await async_client.post("/attempt/", headers=authorized_headers)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Not Found"


@pytest.mark.asyncio
async def test_get_hints_valid_attempt_id(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns the list of hints associated with a valid attempt_id.
    """

    response = await async_client.post("/attempt/2/hints", headers=authorized_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary."
    assert "hints" in data, "Response should include 'hints' key."
    assert len(data["hints"]) > 0, "Hints list should not be empty."


@pytest.mark.asyncio
async def test_get_hints_no_hints_for_attempt(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns an empty list when no hints are associated with the attempt_id.
    """
    response = await async_client.post(
        "/attempt/4/hints", headers=authorized_headers
    )  # Assume 2 has no hints
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary."
    assert "hints" in data, "Response should include 'hints' key."
    assert len(data["hints"]) == 0, "Hints list should be empty."


@pytest.mark.asyncio
async def test_get_hints_invalid_attempt_id(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint responds with a 404 Not Found status code when an invalid attempt_id is provided.
    """
    response = await async_client.post(
        "/attempt/99999/hints", headers=authorized_headers
    )  # Non-existent attempt_id
    assert response.status_code == 404
    assert (
        response.json()["detail"] == "Attempt with 99999 id does not exist [EscapeRoom]"
    )


@pytest.mark.asyncio
async def test_get_hints_unauthorized_access(async_client: AsyncClient):
    """
    Test that an unauthorized user cannot access the get_hints endpoint.
    """
    response = await async_client.post("/attempt/1/hints")
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_get_hints_with_access_to_other_user_attempt(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint responds with a 403 Forbidden status code when a user tries to access hints for
    an attempt_id that belongs to another user.
    """
    response = await async_client.post(
        "/attempt/5/hints", headers=authorized_headers
    )  # Assume attempt 1 belongs to user1
    assert response.status_code == 401
    assert "detail" in response.json()
    assert (
        response.json()["detail"]
        == "User doesn't have access to this attempt [EscapeRoom]"
    )
