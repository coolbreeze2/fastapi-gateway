import os

from fastapi_users.password import PasswordHelper
from typing import Dict, Any, Optional, Type, Generic, List, Tuple

from fastapi_users.models import UP, ID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from fastapi_gateway.server.database import async_session
from fastapi_gateway.server.models import User


async def create_admin_user():
    async with async_session() as session:
        user_db = SQLAlchemyUserDatabase(session, User)
        user = await user_db.get_by_username("admin")
        password = os.getenv("ADMIN_PASSWORD") or "123456"
        hashed_password = PasswordHelper().hash(password)
        if not user:
            await user_db.create({
                "email": "admin@123.com",
                "username": "admin",
                "hashed_password": hashed_password,
                "name": "admin",
                "roles": ["Admin"],
                "is_superuser": True
            })


class SQLAlchemyUserDatabase(Generic[UP, ID]):
    """
    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    """

    session: AsyncSession
    user_table: Type[UP]

    def __init__(
        self,
        session: AsyncSession,
        user_table: Type[UP],
    ):
        self.session = session
        self.user_table = user_table

    async def pagination(self, dbmodel, page: int = 1, limit=10):
        statement = select(dbmodel).limit(limit).offset((page - 1) * limit)
        results = (await self.session.scalars(statement)).all()
        total_statement = select(func.count(dbmodel.id))
        total = (await self.session.execute(total_statement)).scalar_one()
        return results, total

    async def list(self, page: int = 1, limit: int = 10) -> Tuple[Optional[List[User]], int]:
        users, total = await self.pagination(self.user_table, page=page, limit=limit)
        return users, total

    async def get(self, id: ID) -> Optional[User]:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_username(self, username: str) -> Optional[User]:
        statement = select(self.user_table).where(
            self.user_table.username == username
        )
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_email_or_username(email)

    async def get_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        statement = select(self.user_table).where(or_(
            func.lower(self.user_table.email) == func.lower(email_or_username),
            self.user_table.username == email_or_username)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: Dict[str, Any]) -> User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        return user

    async def delete(self, user: UP) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> Optional[User]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
