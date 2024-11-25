import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_story import get_all_stories


@pytest.mark.asyncio
async def test_get_all_stories_success(session: AsyncSession):
    """Retrive all stories prepare with conftest 3 Stories"""
    stories = await get_all_stories(session)

    assert stories is not None
    assert len(stories) == 3
