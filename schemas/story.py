from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StoryDisplay(BaseModel):
    title: str
    description: str
    type: str
    difficulty: str
    rating: Optional[float] = None
    cost: int
    create_date: datetime
