import asyncio

from fastapi_users.password import PasswordHelper

from fastapi_gateway.server.curd import SQLAlchemyUserDatabase
from fastapi_gateway.server.database import create_db_and_tables, async_session
from fastapi_gateway.server.models import User


async def gen_mock_data():
    await create_db_and_tables()

    session = async_session()

    user_db = SQLAlchemyUserDatabase(session, User)
    username_prefix = "test-mock"
    password = PasswordHelper().hash("123456")

    for i in range(1, 20):
        await user_db.create({
            "username": f"{username_prefix}{i}",
            "name": f"{username_prefix}{i}",
            "hashed_password": password,
            "email": f"{username_prefix}{i}@123.com"})


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gen_mock_data())
