import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from db.database import create_db_and_tables, get_async_session, get_user_db, engine
from db.models import Base, User
from db.extended_user_database import ExtendedSQLAlchemyUserDatabase
from sqlalchemy.sql import text


@pytest.mark.asyncio
async def test_database_connection():
    """Test that the database engine connects successfully."""
    try:
        # Test the connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError as e:
        pytest.fail(f"Could not connect to the database: {e}")


@pytest.mark.asyncio
async def test_create_db_and_tables():
    """Test that create_db_and_tables creates all tables successfully."""
    async with engine.begin() as conn:
        # Ensure no tables exist before creation
        await conn.run_sync(Base.metadata.drop_all)

    # Call the function to create tables
    await create_db_and_tables()

    async with engine.begin() as conn:
        # Verify tables exist
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result]
        # Replace 'user' with the table names in your models
        expected_tables = ["user"]  # Example table names
        for table in expected_tables:
            assert table in tables


@pytest.mark.asyncio
async def test_get_async_session():
    """Test that get_async_session yields a valid AsyncSession."""
    async for session in get_async_session():
        assert isinstance(session, AsyncSession)
        # Test session functionality with a basic query
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_user_db():
    """Test that get_user_db yields a ExtendedSQLAlchemyUserDatabase instance."""
    async for session in get_async_session():
        async for user_db in get_user_db(session):
            assert user_db is not None
            assert isinstance(user_db, ExtendedSQLAlchemyUserDatabase)
