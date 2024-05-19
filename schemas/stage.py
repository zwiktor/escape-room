from pydantic import BaseModel


class StageDisplay(BaseModel):
    name: str
    level: int
    question: str


class StageBase(BaseModel):
    name: str
    level: int
    question: str
    password: str
    story_id: int

