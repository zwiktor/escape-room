from fastapi import Depends, FastAPI
from starlette.requests import Request
from routers import story, stage, attempt

from db.models import User
from db.database import create_db_and_tables, get_async_session
from users.schemas import UserCreate, UserRead, UserUpdate
from users.auth import auth_backend
from users.manager import current_active_user, fastapi_users
from populate_data import populate_data
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(story.router)
app.include_router(stage.router)
app.include_router(attempt.router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/redis", tags=["auth"]
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
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


@app.get("/")
async def home_page():
    return {"message": "hello world"}


@app.get("/load-data")
async def home_page(db: AsyncSession = Depends(get_async_session)):
    var = await populate_data(db)
    return {"message": f"{var}"}


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
