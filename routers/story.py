from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.database import get_async_session
from schemas.story import StoryDisplay
from db.db_story import get_all_stories


router = APIRouter(
    prefix='/story',
    tags=['story']
)


@router.get('/', response_model=List[StoryDisplay])
async def get_all_blogs(db: AsyncSession = Depends(get_async_session)):
    all_stories = await get_all_stories(db)
    return all_stories
