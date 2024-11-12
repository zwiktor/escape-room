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
async def get_story(story_id: int, db: AsyncSession = Depends(get_async_session)):
    story = await db_story.get_story(story_id, db)
    return story


@router.post("/{story_id}/buy/", response_model=AccessBase)
async def get_story(
    story_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    story_access = await db_story.buy_story(db, story_id, user)
    return story_access


@router.post("/{story_id}/start/", response_model=AttemptBase)
async def get_story(
    story_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    attempt = await db_story.start_story(db, story_id, user)
    return attempt


@router.post("/{story_id}/access/", response_model=StoryStatus)
async def check_access(
    story_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    story_status = await db_access.check_status(db, user, story_id)
    return story_status

    # if story_access is None:
    #     return {
    #         'purchase_date': story_access.purchase_date,
    #         'current_attempt': curr_attempt
    #     }
    #
    # curr_attempt = await db_access.current_attempt(db, user, story_access)
    # return {
    #     'purchase_date': story_access.purchase_date,
    #     'current_attempt': curr_attempt
    # }
