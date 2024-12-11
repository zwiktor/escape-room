import pytest
from httpx import AsyncClient
from fastapi import status


async def login_and_get_token(
    async_client: AsyncClient,
    username: str = "user1@example.com",
    password: str = "hashed1",
) -> str:
    """
    Logs in a user and returns the access token.

    :param async_client: The test client for sending requests.
    :param username: The username (email) of the user.
    :param password: The password of the user.
    :return: The access token as a string.
    """
    response = await async_client.post(
        "/auth/redis/login",
        data={
            "grant_type": "",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_user_success(async_client: AsyncClient):
    """
    Test logging in with valid credentials.
    """
    response = await async_client.post(
        "/auth/redis/login",
        data={
            "grant_type": "",
            "username": "user1@example.com",
            "password": "hashed1",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected 200 but got {response.status_code}"
    data = response.json()
    assert "access_token" in data, "Response should contain an access token."
    assert data["token_type"] == "bearer", "Token type should be 'bearer'."


@pytest.mark.asyncio
async def test_login_user_unvalid_password(async_client: AsyncClient):
    """
    Test logging in with an invalid password.
    """
    response = await async_client.post(
        "/auth/redis/login",
        data={
            "grant_type": "",
            "username": "user1@example.com",
            "password": "wrongpassword",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
    ), f"Expected 400 but got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Response should contain a detail message."
    assert (
        data["detail"] == "LOGIN_BAD_CREDENTIALS"
    ), "Error message should indicate invalid credentials."


@pytest.mark.asyncio
async def test_login_user_does_not_exists(async_client: AsyncClient):
    """
    Test logging in with a non-existent user.
    """
    response = await async_client.post(
        "/auth/redis/login",
        data={
            "grant_type": "",
            "username": "nonexistent@example.com",
            "password": "hashed1",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
    ), f"Expected 400 but got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Response should contain a detail message."
    assert (
        data["detail"] == "LOGIN_BAD_CREDENTIALS"
    ), "Error message should indicate invalid credentials."
