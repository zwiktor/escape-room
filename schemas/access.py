from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AttemptBase(BaseModel):
    id: int
    story_access_id: int
    stage_id: int
    start_date: datetime
    finish_date: Optional[datetime]


class StoryAccessBase(BaseModel):
    # id: int
    # story_id: int
    purchase_date: datetime
    current_attempt: Optional[AttemptBase]
