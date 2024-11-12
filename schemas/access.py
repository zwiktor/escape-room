from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID


class StatusEnum(str, Enum):
    new = "new"
    purchased = "purchased"
    started = "started"
    ended = "finished"


class AttemptBase(BaseModel):
    id: int
    story_access_id: int
    stage_id: int
    start_date: datetime
    finish_date: Optional[datetime]


class AccessBase(BaseModel):
    id: int
    user_id: UUID
    story_id: int
    purchase_date: datetime


class StoryAccessBase(BaseModel):
    purchase_date: Optional[datetime]
    current_attempt: Optional[AttemptBase]


class StoryStatus(BaseModel):
    status: StatusEnum
    story_access: Optional[StoryAccessBase]
