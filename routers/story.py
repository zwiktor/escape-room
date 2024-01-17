from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.database import get_async_session
from schemas.story import StoryDisplay, StoryBase
from db import db_story


router = APIRouter(
    prefix='/story',
    tags=['story']
)


@router.get('/{story_id}', response_model=StoryDisplay)
async def get_story(story_id: int, db: AsyncSession = Depends(get_async_session)):
    story = await db_story.get_story(story_id, db)
    return story


@router.get('/', response_model=List[StoryDisplay])
async def get_all_stories(db: AsyncSession = Depends(get_async_session)):
    stories = await db_story.get_all_stories(db)
    return stories


@router.post('/new/', response_model=StoryDisplay)
async def create_story(request: StoryDisplay, db: AsyncSession = Depends(get_async_session)):
    story = await db_story.create_story(db, request)
    return story



