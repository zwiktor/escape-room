from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.database import get_async_session
from schemas.stage import StageDisplay, StageBase
from schemas.story import StoryBase
from db import db_stage

router = APIRouter(
    prefix='/stage',
    tags=['stage']
)


@router.post('/', response_model=List[StageDisplay])
async def get_stages(request: StoryBase, db: AsyncSession = Depends(get_async_session)):
    stages = await db_stage.get_stages(request, db)
    return stages


@router.post('/{stage_level}', response_model=StageDisplay)
async def get_stages(request: StoryBase,
                     stage_level: int,
                     db: AsyncSession = Depends(get_async_session)):
    stage = await db_stage.get_stage(request, stage_level, db)
    return stage


