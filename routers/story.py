from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
import time

from db.database import get_async_session
from schemas.story import StoryDisplay, StoryBase
from schemas.access import StoryAccessBase, StoryStatus, AttemptBase, AccessBase
from db import db_story
from db import db_access
from db.models import User
from db.storymanager import get_story_manager, StoryManager

from users.manager import current_active_user

router = APIRouter(prefix="/story", tags=["story"])


@router.get("/", response_model=List[StoryBase])
async def get_all_stories(db: AsyncSession = Depends(get_async_session)):
    stories = await db_story.get_all_stories(db)
    return stories


@router.post("/new/", response_model=StoryDisplay)
async def create_story(
    request: StoryDisplay, db: AsyncSession = Depends(get_async_session)
):
    story = await db_story.create_story(db, request)
    return story


@router.post("/{story_id}", response_model=StoryBase)
async def get_story(
    story_id: int,
    story_manager: StoryManager = Depends(get_story_manager),
    user: User = Depends(current_active_user),
):
    await story_manager.load_by_story_id(story_id=story_id)
    return await story_manager.get_story()


@router.post("/{story_id}/buy/", response_model=StoryStatus)
async def get_story(
    story_id: int, story_manager: StoryManager = Depends(get_story_manager)
):
    await story_manager.load_by_story_id(story_id)
    await story_manager.buy_story()
    response = await story_manager.check_access()
    return response


@router.post("/{story_id}/start/", response_model=StoryStatus)
async def get_story(
    story_id: int, story_manager: StoryManager = Depends(get_story_manager)
):
    await story_manager.load_by_story_id(story_id)
    await story_manager.start_story()
    response = await story_manager.check_access()
    return response


@router.post("/{story_id}/access/", response_model=StoryStatus)
async def check_access(
    story_id: int, story_manager: StoryManager = Depends(get_story_manager)
):
    await story_manager.load_by_story_id(story_id)
    response = await story_manager.check_access()
    return response
