from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

from app.schemas.stage import StageDisplay


class HintBase(BaseModel):
    text: str
    trigger: str

    model_config = ConfigDict(from_attributes=True)


class HintsDisplay(BaseModel):
    hints: List[HintBase]

    model_config = ConfigDict(from_attributes=True)


class AttemptDisplay(BaseModel):
    start_date: datetime
    stage: StageDisplay
    is_finished: Optional[bool]


class PasswordFormBase(BaseModel):
    password: str


class PasswordCheckDisplay(BaseModel):
    message: str
    new_hint: bool = False
    next_attempt: Optional[int] = None
    end_story: bool = False
