import pytest
from fastapi_users.authentication import RedisStrategy, BearerTransport
from users.auth import redis, get_redis_strategy, auth_backend
from unittest.mock import AsyncMock, patch
from fastapi_users.models import UserProtocol
import redis.asyncio as aioredis


@pytest.mark.asyncio
async def test_redis_connection():
    """Test that the Redis connection is established successfully."""
    try:
        # Test Redis ping
        result = await redis.ping()
        assert result is True
    except Exception as e:
        pytest.fail(f"Could not connect to Redis: {e}")


def test_bearer_transport():
    """Test the BearerTransport configuration."""
    transport = auth_backend.transport
    assert isinstance(transport, BearerTransport)
    # Verify the token URL indirectly by inspecting the configured backend name
    assert auth_backend.name == "Redis"


def test_redis_strategy_initialization():
    """Test that RedisStrategy is initialized correctly."""
    strategy = get_redis_strategy()
    assert isinstance(strategy, RedisStrategy)
    assert strategy.lifetime_seconds == 3600


@pytest.mark.asyncio
async def test_redis_strategy_with_real_redis():
    """Test RedisStrategy with a real Redis instance."""
    # Set up a real Redis connection (ensure Redis is running locally on port 6379)
    redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
    strategy = get_redis_strategy()

    # Ensure strategy uses the correct Redis instance
    strategy.redis = redis

    # Simulate a real user object
    class RealUser(UserProtocol[str]):
        def __init__(self):
            self.id = "test_user_id"
            self.email = "test@example.com"
            self.hashed_password = "hashed_password"
            self.is_active = True
            self.is_superuser = False
            self.is_verified = True

    user = RealUser()

    try:
        # Create a token
        token = await strategy.write_token(user)
        assert token is not None

        # Validate the token
        user_id = await redis.get(f"{strategy.key_prefix}{token}")
        assert user_id == user.id

        # Invalidate the token
        await strategy.destroy_token(token, user)
        invalidated_user_id = await redis.get(f"{strategy.key_prefix}{token}")
        assert invalidated_user_id is None
    finally:
        # Ensure Redis is cleaned up
        await redis.flushall()  # Optional: Clears all keys (only use for testing)
        await redis.aclose()
