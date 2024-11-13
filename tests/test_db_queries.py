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
async def test_create_instance_bad_data(session: AsyncSession):
    """Test create_instance with invalid data, expecting an IntegrityError due to an empty username."""

    with pytest.raises(IntegrityError):
        # Attempt to create a user with an empty username, which should raise an IntegrityError
        await create_instance(
            session,
            User,
            email="create@example.com",
            username="",  # Invalid data: empty username
            hashed_password="hashed",
        )

    # Rollback the session to clean up after the IntegrityError
    await session.rollback()


@pytest.mark.asyncio
async def test_get_instance_found(session: AsyncSession):
    # Arrange: Create a user in the database
    user = User(
        email="findme@example.com",
        username="find_me",
        hashed_password="hashed_password",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Act: Retrieve the user by email
    result = await get_instance(session, User, email="findme@example.com")

    # Assert: The user should be found and match the created instance
    assert result is not None
    assert result.email == "findme@example.com"
    assert result.username == "find_me"


@pytest.mark.asyncio
async def test_get_instance_not_found(session: AsyncSession):
    # Act: Attempt to retrieve a user that doesn't exist
    result = await get_instance(session, User, email="nonexistent@example.com")

    # Assert: No user should be found, so result should be None
    assert result is None


@pytest.mark.asyncio
async def test_get_instance_multiple_matches_raises_error(session: AsyncSession):
    # Arrange: Create multiple users with the same non-unique attribute, e.g., `is_active`
    user1 = User(
        email="active1@example.com",
        username="active_user1",
        hashed_password="hashed_password1",
        is_active=True,
    )
    user2 = User(
        email="active2@example.com",
        username="active_user2",
        hashed_password="hashed_password2",
        is_active=True,
    )
    session.add(user1)
    session.add(user2)
    await session.commit()

    # Act & Assert: Attempt to retrieve a single instance by `is_active=True` and expect MultipleResultsException
    with pytest.raises(MultipleResultsException):
        await get_instance(session, User, is_active=True)


@pytest.mark.asyncio
async def test_get_instances_basic_retrieval(session):
    # Arrange: Create multiple users with is_active=True
    user1 = User(
        email="active10@example.com",
        username="user10",
        hashed_password="hashed_password1",
        is_active=True,
    )
    user2 = User(
        email="active20@example.com",
        username="user20",
        hashed_password="hashed_password2",
        is_active=True,
    )
    user3 = User(
        email="inactive@example.com",
        username="user30",
        hashed_password="hashed_password3",
        is_active=False,
    )
    session.add_all([user1, user2, user3])
    await session.commit()

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
        session, User, is_active=True, username="user20"
    )

    # Assert: Only the active user with username "unique_multi_user1" should be retrieved
    assert len(filtered_users) == 1
    assert filtered_users[0].username == "user20"
    assert filtered_users[0].is_active is True


@pytest.mark.asyncio
async def test_get_instances_list_filter(session):
    # Act: Retrieve users with usernames in the specified list
    users_in_list = await get_instances(session, User, username=["user10", "user20"])

    # Assert: Only users with usernames "user10" and "user20" should be retrieved
    assert len(users_in_list) == 2
    assert {user.username for user in users_in_list} == {"user10", "user20"}
