import uuid

from pydantic import BaseModel
from fastapi_users import schemas
from typing import Optional


class LoginRequest(BaseModel):
    identifier: str  # Accepts email or username
    password: str


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str]
