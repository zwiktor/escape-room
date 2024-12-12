from fastapi import Depends, FastAPI, status
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.routers import story
from app.routers import attempt
from typing import Callable, Any, Coroutine

from app.db.models import User
from app.db.database import create_db_and_tables, get_async_session
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.manager import current_active_user, fastapi_users
from app.users.auth import auth_backend
from populate_data import populate_data
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.exceptions.exceptions import (
    EscapeRoomError,
    InsufficientGoldError,
    StoryAlreadyOwnedError,
    EntityDoesNotExistError,
    StoryAlreadyStartedError,
    UnAuthenticatedUserError,
    EmptyPasswordFormError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Database setup
    await create_db_and_tables()
    yield
    # Shutdown: Any necessary cleanup (if required)


app = FastAPI(lifespan=lifespan)

app.include_router(story.router)
app.include_router(attempt.router)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/redis",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.name or user.email}!"}


@app.get("/")
async def home_page():
    return {"message": "hello world"}


@app.get("/load-data")
async def home_page(db: AsyncSession = Depends(get_async_session)):
    var = await populate_data(db)
    return {"message": f"{var}"}


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, EscapeRoomError], Coroutine[Any, Any, JSONResponse]]:
    detail = {"message": initial_detail}  # Using a dictionary to hold the detail

    async def exception_handler(_: Request, exc: EscapeRoomError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        return JSONResponse(
            status_code=status_code, content={"detail": detail["message"]}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=StoryAlreadyOwnedError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "User already have acces to the story."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InsufficientGoldError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "Not enough gold to handle transaction"
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=StoryAlreadyStartedError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "User already have started story"
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=EntityDoesNotExistError,
    handler=create_exception_handler(
        status.HTTP_404_NOT_FOUND, "Entity doesn't found in database"
    ),
)
app.add_exception_handler(
    exc_class_or_status_code=UnAuthenticatedUserError,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, "user unauthorized for this opperation"
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=EmptyPasswordFormError,
    handler=create_exception_handler(
        status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid passwrod for attempt"
    ),
)
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
