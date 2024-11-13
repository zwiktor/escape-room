import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.models import User, Story
from db.db_queries import (
    convert_to_pydantic,
    get_instance,
    get_last_instance,
    create_instance,
    get_or_create,
    get_instances,
    MultipleResultsException,
)
from pydantic import BaseModel


@pytest.mark.asyncio
async def test_create_instance(session: AsyncSession):
    # Testowanie create_instance
    user = await create_instance(
        session,
        User,
        email="create@example.com",
        username="create_user",
        hashed_password="hashed",
    )
    assert user is not None
    assert user.email == "create@example.com"
    assert user.username == "create_user"


@pytest.mark.asyncio
async def test_create_instance_missing_username(session: AsyncSession):
    """Test create_instance with invalid data, expecting a ValueError due to an empty username."""
    with pytest.raises(ValueError, match="Username cannot be empty."):
        # Attempt to create a user with an empty username, which should raise a ValueError
        await create_instance(
            session,
            User,
            email="createunvalid@example.com",
            username="",  # Invalid data: empty username
            hashed_password="hashed2",
        )
        # Use flush to ensure the constraint check is applied immediately
        await session.flush()
    # Rollback the session to clean up after the ValueError
    await session.rollback()


@pytest.mark.asyncio
async def test_create_instance_missing_email(session: AsyncSession):
    """Test create_instance with invalid data, expecting a ValueError due to an empty email."""
    with pytest.raises(ValueError, match="Email cannot be empty."):
        # Attempt to create a user with an empty email, which should raise a ValueError
        await create_instance(
            session,
            User,
            email="",  # Invalid data: empty email
            username="username123",
            hashed_password="hashed2",
        )
        # Use flush to trigger the constraint check
        await session.flush()
    # Rollback the session to clean up after the ValueError
    await session.rollback()


@pytest.mark.asyncio
async def test_get_instance_found(session: AsyncSession):
    # Act: Retrieve the user by email
    result = await get_instance(session, User, email="user2@example.com")

    # Assert: The user should be found and match the created instance
    assert result is not None
    assert result.email == "user2@example.com"
    assert result.username == "user2"


@pytest.mark.asyncio
async def test_get_instance_not_found(session: AsyncSession):
    # Act: Attempt to retrieve a user that doesn't exist
    result = await get_instance(session, User, email="nonexistent@example.com")

    # Assert: No user should be found, so result should be None
    assert result is None


@pytest.mark.asyncio
async def test_get_instance_multiple_matches_raises_error(session: AsyncSession):
    # Act & Assert: Attempt to retrieve a single instance by `is_active=True` and expect MultipleResultsException
    with pytest.raises(MultipleResultsException):
        await get_instance(session, User, is_active=True)


@pytest.mark.asyncio
async def test_get_instances_basic_retrieval(session):
    # Act: Retrieve all users with is_active=True
    active_users = await get_instances(session, User, is_active=True)

    # Assert: Only two users should be retrieved
    assert len(active_users) > 1
    assert all(user.is_active for user in active_users)


@pytest.mark.asyncio
async def test_get_instances_empty_result(session):
    # Act: Attempt to retrieve users with a non-existent email
    non_existent_users = await get_instances(
        session, User, email="noone_unique@example.com"
    )

    # Assert: No users should be found, so the result should be an empty list
    assert non_existent_users == []


@pytest.mark.asyncio
async def test_get_instances_multiple_filters(session):
    # Act: Retrieve active users with the username "unique_multi_user1"
    filtered_users = await get_instances(
        session, User, is_active=True, username="user2"
    )

    # Assert: Only the active user with username "unique_multi_user1" should be retrieved
    assert len(filtered_users) == 1
    assert filtered_users[0].username == "user2"
    assert filtered_users[0].is_active is True


@pytest.mark.asyncio
async def test_get_instances_list_filter(session):
    # Act: Retrieve users with usernames in the specified list
    users_in_list = await get_instances(session, User, username=["user1", "user2"])

    # Assert: Only users with usernames "user10" and "user20" should be retrieved
    assert len(users_in_list) == 2
    assert {user.username for user in users_in_list} == {"user1", "user2"}


@pytest.mark.asyncio
async def test_get_or_create_retrieve_existing_instance(session: AsyncSession):
    """Test get_or_create retrieves an existing instance if it matches the criteria."""
    user = await get_or_create(
        session, User, username="user2", email="user2@example.com"
    )

    # Assert: The function should return the existing user, not create a new one
    assert user.email == "user2@example.com"
    assert user.username == "user2"


@pytest.mark.asyncio
async def test_get_or_create_create_new_instance(session: AsyncSession):
    """Test get_or_create creates a new instance if no match exists."""

    # Act: Attempt to get_or_create a User that does not exist
    new_user = await get_or_create(
        session,
        User,
        email="newuser@example.com",
        username="new_user",
        hashed_password="hashed_password",
    )

    # Assert: A new user should be created with the specified email and username
    assert new_user is not None
    assert new_user.email == "newuser@example.com"
    assert new_user.username == "new_user"

    # Verify that the user was actually committed in the session
    await session.flush()
    retrieved_user = await session.get(User, new_user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "newuser@example.com"
    assert retrieved_user.username == "new_user"


@pytest.mark.asyncio
async def test_get_last_instance(session: AsyncSession):
    """Test get_last_instance retrieves the last added object it matches the criteria."""
    user = await get_last_instance(session, User, "username")

    # Assert: The function should return the existing user, not create a new one
    assert user.email == "user4@example.com"
    assert user.username == "user4"
