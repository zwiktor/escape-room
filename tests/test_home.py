import pytest
from httpx import AsyncClient
from main import app  # Replace with your actual FastAPI app module


@pytest.mark.asyncio
async def test_home(async_client):
    """Test the home endpoint."""
    response = await async_client.get("/")  # Use 'await' to call async methods
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}
