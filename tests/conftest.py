import pytest
import json
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.models import *
from users.manager import get_user_manager
from pathlib import Path
from datetime import datetime
import logging
from httpx import ASGITransport, AsyncClient
from main import app
import redis.asyncio as aioredis
from db.extended_user_database import ExtendedSQLAlchemyUserDatabase
from db.models import User
from fastapi_users.password import PasswordHelper
from db.db_queries import get_instance
from db.storymanager import StoryManager


REDIS_URL = "redis://localhost:6379/0"
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# Tworzymy asynchroniczny silnik i konfigurujemy sesję
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


# Fixture do tworzenia tabel przed testami
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    # Step 1: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Step 2: Load JSON data and populate tables
    json_path = Path(__file__).parent / "test_data.json"
    with open(json_path) as f:
        data = json.load(f)

        async with AsyncSessionLocal() as session:
            # Populate User data
            users = {
                user_data["email"]: User(**user_data) for user_data in data["users"]
            }
            session.add_all(users.values())
            await session.commit()
            # Populate Story data
            stories = {
                story_data["title"]: Story(**story_data)
                for story_data in data["stories"]
            }
            session.add_all(stories.values())
            await session.commit()
            # Populate Stage data and link to Story
            stages = {
                stage_data["name"]: Stage(
                    **{k: v for k, v in stage_data.items() if k != "story_title"},
                    story=stories[stage_data["story_title"]]
                )
                for stage_data in data["stages"]
            }
            session.add_all(stages.values())
            await session.commit()
            # Populate StoryAccess data and link to User and Story
            story_accesses = [
                StoryAccess(
                    user=users[access_data["user_email"]],
                    story=stories[access_data["story_title"]],
                    purchase_date=datetime.fromisoformat(access_data["purchase_date"]),
                )
                for access_data in data["story_accesses"]
            ]
            session.add_all(story_accesses)
            await session.commit()
            # Populate Attempt data and link to StoryAccess and Stage
            attempts = [
                Attempt(
                    access=next(
                        sa
                        for sa in story_accesses
                        if sa.user.email == attempt_data["story_access_user_email"]
                        and sa.story.title == attempt_data["story_access_story_title"]
                    ),
                    stage=stages[attempt_data["stage_name"]],
                    start_date=datetime.fromisoformat(attempt_data["start_date"]),
                    # Convert string to datetime
                    finish_date=(
                        datetime.fromisoformat(attempt_data["finish_date"])
                        if attempt_data.get("finish_date")
                        else None
                    ),
                )
                for attempt_data in data["attempts"]
            ]
            session.add_all(attempts)
            await session.commit()
            # Populate Hint data and link to Stage
            hints = {
                hint_data["text"]: Hint(
                    **{k: v for k, v in hint_data.items() if k != "stage_name"},
                    stage=stages[hint_data["stage_name"]]
                )
                for hint_data in data["hints"]
            }
            session.add_all(hints.values())
            await session.commit()

            # Populate PasswordAttempt data and link to Attempt
            password_attempts = [
                PasswordAttempt(
                    attempt=next(
                        a
                        for a in attempts
                        if a.access.user.email
                        == attempt_data["attempt_story_access_user_email"]
                        and a.access.story.title
                        == attempt_data["attempt_story_access_story_title"]
                        and a.stage.name == attempt_data["attempt_stage_name"]
                    ),
                    password=attempt_data["password"],
                    enter_date=datetime.fromisoformat(attempt_data["enter_date"]),
                )
                for attempt_data in data["password_attempts"]
            ]
            session.add_all(password_attempts)
            await session.commit()

            # Populate HintsAttempt data and link to Attempt and Hint
            hints_attempts = [
                HintsAttempt(
                    attempt=next(
                        a
                        for a in attempts
                        if a.access.user.email
                        == attempt_data["attempt_story_access_user_email"]
                        and a.access.story.title
                        == attempt_data["attempt_story_access_story_title"]
                        and a.stage.name == attempt_data["attempt_stage_name"]
                    ),
                    hint=hints[attempt_data["hint_text"]],
                    enter_date=datetime.fromisoformat(attempt_data["enter_date"]),
                )
                for attempt_data in data["hints_attempts"]
            ]
            session.add_all(hints_attempts)
            await session.commit()
    # Yield control back to the tests
    yield

    # Cleanup: Drop all tables after the tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Asynchroniczny fixture sesji
@pytest_asyncio.fixture
async def session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def redis_client():
    """Provide a Redis client for testing."""
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    await redis.flushdb()  # Clear Redis before each test
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture(scope="function", autouse=True)
def suppress_sqlalchemy_logs():
    """Suppress SQLAlchemy logs."""
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


@pytest_asyncio.fixture
async def async_client():
    """Fixture for the HTTPX AsyncClient."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def user_manager(session: AsyncSession):
    user_db = ExtendedSQLAlchemyUserDatabase(session, User)
    # Optionally prepopulate users
    password_helper = PasswordHelper()
    raw_password = "test_password"
    hashed_password = password_helper.hash(raw_password)

    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        gold=1,
        is_active=1,
        is_superuser=0,
        is_verified=1,
    )
    session.add(test_user)
    await session.commit()

    async for manager in get_user_manager(user_db=user_db):
        yield manager


@pytest_asyncio.fixture
async def mock_user(session: AsyncSession):
    return await get_instance(session, User, username="user1")


@pytest_asyncio.fixture
async def story_manager(session: AsyncSession, mock_user: User):
    """Fixture for creating a StoryManager instance."""
    return StoryManager(session, mock_user)
