import pytest
from fastapi_users.exceptions import UserNotExists
from app.users.manager import UserManager
from fastapi.security import OAuth2PasswordRequestForm


@pytest.mark.asyncio
async def test_get_by_email_or_username(user_manager: UserManager):
    """Test retrieving a user by email or username."""

    # Retrieve by email
    user_by_email = await user_manager.get_by_username_or_email("test@example.com")
    assert user_by_email.email == "test@example.com"
    assert user_by_email.username == "testuser"

    # Retrieve by username
    user_by_username = await user_manager.get_by_username_or_email("testuser")
    assert user_by_username.email == "test@example.com"
    assert user_by_username.username == "testuser"

    # Test non-existent user
    with pytest.raises(UserNotExists):
        await user_manager.get_by_username_or_email("nonexistent")


@pytest.mark.asyncio
async def test_authenticate_success_with_email(user_manager: UserManager):
    """Test successful authentication with valid email and password."""
    raw_password = "test_password"

    credentials = OAuth2PasswordRequestForm(
        username="test@example.com", password=raw_password
    )
    authenticated_user = await user_manager.authenticate(credentials)

    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    assert authenticated_user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_success_with_username(user_manager: UserManager):
    """Test successful authentication with valid email and password."""
    raw_password = "test_password"

    credentials = OAuth2PasswordRequestForm(username="testuser", password=raw_password)
    authenticated_user = await user_manager.authenticate(credentials)

    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    assert authenticated_user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_invalid_password_email(user_manager: UserManager):
    wrong_password = "correct_password"

    credentials = OAuth2PasswordRequestForm(
        username="test@example.com", password="wrong_password"
    )
    authenticated_user = await user_manager.authenticate(credentials)

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_invalid_password_username(user_manager: UserManager):
    wrong_password = "correct_password"

    credentials = OAuth2PasswordRequestForm(
        username="testuser", password="wrong_password"
    )
    authenticated_user = await user_manager.authenticate(credentials)

    assert authenticated_user is None
