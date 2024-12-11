from sqlalchemy import or_, func
from sqlalchemy.future import select
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.db.models import User
from typing import Optional


class ExtendedSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """
        Get a user by email or username.

        :param identifier: Email or username of the user to retrieve.
        :return: A user object or None if not found.
        """
        statement = select(self.user_table).where(
            or_(
                func.lower(self.user_table.email) == func.lower(identifier),
                self.user_table.username == identifier,
            )
        )
        return await self._get_user(statement)
