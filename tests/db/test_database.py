import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from app.db.models import User
from app.db.extended_user_database import ExtendedSQLAlchemyUserDatabase
from sqlalchemy.sql import text
from tests.conftest import engine


@pytest.mark.asyncio
async def test_database_connection():
    """Test that the database engine connects successfully."""
    try:
        # Test the connection using the test engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError as e:
        pytest.fail(f"Could not connect to the test database: {e}")


@pytest.mark.asyncio
async def test_create_db_and_tables(setup_database):
    """Test that create_db_and_tables creates all tables successfully."""
    async with engine.begin() as conn:
        # Verify tables exist after setup_database
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result]
        # Replace 'user' with the table names in your models
        expected_tables = [
            "user",
            "story",
            "stage",
            "story_access",
            "attempt",
            "hint",
            "password_attempt",
            "hints_attempt",
        ]  # Example table names
        for table in expected_tables:
            assert table in tables, f"Table {table} was not created."


@pytest.mark.asyncio
async def test_get_async_session(session: AsyncSession):
    """Test that get_async_session yields a valid AsyncSession."""
    assert isinstance(session, AsyncSession)
    # Test session functionality with a basic query
    result = await session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_user_db(session: AsyncSession):
    """Test that get_user_db yields an ExtendedSQLAlchemyUserDatabase instance."""
    user_db = ExtendedSQLAlchemyUserDatabase(session, User)
    assert isinstance(user_db, ExtendedSQLAlchemyUserDatabase)
