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


@pytest.mark.asyncio
async def test_password_validation_correct_password(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint validates a correct password, moves to the next stage, and updates the message.
    """
    response = await async_client.post(
        "/attempt/2/check_password",
        headers=authorized_headers,
        json={"password": "seek2"},
    )
    assert response.status_code == 200, "Expected status code to be 200."
    data = response.json()
    assert data["message"] == "Gratulacje, to prawidlowa odpowiedz"
    assert (
        "next_attempt" in data and data["next_attempt"] is not None
    ), "Next attempt ID should be present."


@pytest.mark.asyncio
async def test_password_validation_correct_final_password(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint validates the final password correctly and ends the story.
    """
    response = await async_client.post(
        "/attempt/7/check_password",
        headers=authorized_headers,
        json={"password": "check"},  # Replace with the final test password
    )
    assert response.status_code == 200, "Expected status code to be 200."
    data = response.json()
    assert data["message"] == "Gratulacje, historia zostala zakonczona"
    assert data["end_story"] is True, "Story should be marked as ended."


@pytest.mark.asyncio
async def test_password_validation_invalid_password(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint handles an incorrect password correctly by providing an appropriate message.
    """
    response = await async_client.post(
        "/attempt/1/check_password",
        headers=authorized_headers,
        json={"password": "wrong_password"},
    )
    assert response.status_code == 200, "Expected status code to be 200."
    data = response.json()
    assert data["message"] == "Nieprawidłowa odpowiedź, próbuj dalej"
    assert data["new_hint"] is False, "No new hint should be discovered."
    assert data["next_attempt"] is None, "No next attempt should be initiated."


@pytest.mark.asyncio
async def test_password_validation_new_hint_discovered(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint identifies when a new hint is discovered for the given password.
    """
    response = await async_client.post(
        "/attempt/2/check_password",
        headers=authorized_headers,
        json={
            "password": "give me hint 5"
        },  # Replace with a password that triggers a hint
    )
    assert response.status_code == 200, "Expected status code to be 200."
    data = response.json()
    assert data["message"] == "Nowa wskazowka zostala odkryta"
    assert data["new_hint"] is True, "A new hint should be discovered."


@pytest.mark.asyncio
async def test_password_validation_new_hint_discovered(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint identifies when a new hint is discovered for the given password.
    """
    response = await async_client.post(
        "/attempt/2/check_password",
        headers=authorized_headers,
        json={
            "password": "give me hint 4"
        },  # Replace with a password that triggers a hint
    )
    assert response.status_code == 200, "Expected status code to be 200."
    data = response.json()
    assert data["next_attempt"] is None
    assert data["new_hint"] is False, "A new hint should be discovered."
    assert data["message"] == "Nieprawidłowa odpowiedź, próbuj dalej"


@pytest.mark.asyncio
async def test_password_validation_invalid_attempt_id(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns a 404 error when an invalid attempt ID is provided.
    """
    response = await async_client.post(
        "/attempt/99999/check_password",  # Non-existent attempt ID
        headers=authorized_headers,
        json={"password": "any_password"},
    )
    assert response.status_code == 404, "Expected status code to be 404."
    assert (
        response.json()["detail"] == "Attempt with 99999 id does not exist [EscapeRoom]"
    )


@pytest.mark.asyncio
async def test_password_validation_unauthorized_request(async_client: AsyncClient):
    """
    Test that the endpoint returns a 401 Unauthorized error for requests without a valid token.
    """
    response = await async_client.post(
        "/attempt/1/check_password",
        json={"password": "any_password"},
    )
    assert response.status_code == 401, "Expected status code to be 401."
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_password_validation_no_password_provided(
    async_client: AsyncClient, authorized_headers: dict
):
    """
    Test that the endpoint returns a 422 Unprocessable Entity error when no password is provided.
    """
    response = await async_client.post(
        "/attempt/1/check_password",
        headers=authorized_headers,
        json={},
    )
    assert response.status_code == 422, "Expected status code to be 422."
    data = response.json()
    assert "detail" in data, "Response should contain details about the error."
