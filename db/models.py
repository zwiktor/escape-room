from sqlalchemy.orm import DeclarativeBase
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Base(DeclarativeBase):
    # Here we can add some parameters for User
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
