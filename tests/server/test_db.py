import uuid
from typing import AsyncGenerator

from fastapi_users.password import PasswordHelper

from fastapi_gateway.server.curd import SQLAlchemyUserDatabase, Adapter
from fastapi_gateway.server.database import create_db_and_tables, get_async_session, async_session
from fastapi_gateway.server.middleware.casbin import casbin_model
from fastapi_gateway.server.models import User


async def test_create_db_and_tables():
    await create_db_and_tables()


async def test_get_async_session():
    assert isinstance(get_async_session(), AsyncGenerator)


class TestSQLAlchemyUserDatabase(object):
    _id = uuid.UUID('fe65179a-2bb2-47b2-949c-0837c7918d66')
    username = "test"
    name = "test"
    email = "test@123.com"
    password = PasswordHelper().hash("123456")
    session = async_session()
    user_db = SQLAlchemyUserDatabase(session, User)

    async def test_create(self):
        user = await self.user_db.create({
            "id": self._id,
            "username": self.username,
            "name": self.name,
            "hashed_password": self.password,
            "email": self.email
        })
        assert isinstance(user, User)

    async def test_list(self):
        users, total = await self.user_db.list()
        print(total)
        assert isinstance(users, list)
        assert isinstance(total, int)

    async def test_get(self):
        user = await self.user_db.get(self._id)
        assert user.id == self._id

    async def test_get_by_email(self):
        user = await self.user_db.get_by_email(self.email)
        assert user.email == self.email

    async def test_get_by_username(self):
        user = await self.user_db.get_by_username(self.username)
        assert user.username == self.username

    async def test_get_by_email_or_username(self):
        user = await self.user_db.get_by_email_or_username(self.email)
        assert user.email == self.email
        user = await self.user_db.get_by_email_or_username(self.username)
        assert user.username == self.username

    async def test_update(self):
        user = await self.user_db.get(self._id)
        new_name = "test_new"
        new_user = await self.user_db.update(user, {"name": new_name})
        assert new_user.name == new_name

    async def test_delete(self):
        user = await self.user_db.get(self._id)
        await self.user_db.delete(user)


class TestAdapter(object):
    adapter = Adapter(model=casbin_model)

    async def test_load_policy(self):
        await self.adapter.load_policy()

    async def test_load_filtered_policy(self):
        # TODO
        pass

    async def test_filter_query(self):
        # TODO
        pass

    async def test__save_policy_line(self):
        # TODO
        pass

    async def test_save_policy(self):
        await self.adapter.load_policy()
        await self.adapter.save_policy()

    async def test_add_policy(self):
        rule = ["admin", "domain1", "data1", "read"]
        await self.adapter.load_policy()
        await self.adapter.add_policy("p", "p", rule)

    async def test_add_policies(self):
        rules = [
            ["admin", "domain1", "data1", "read"],
            ["admin", "domain1", "data1", "write"]
        ]
        await self.adapter.load_policy()
        await self.adapter.add_policies("p", "p", rules)

    async def test_remove_policy(self):
        # TODO
        pass

    async def test_remove_policies(self):
        # TODO
        pass

    async def test_remove_filtered_policy(self):
        # TODO
        pass

    async def test_update_policy(self):
        # TODO
        pass

    async def test_update_filtered_policies(self):
        # TODO
        pass

    async def test__update_filtered_policies(self):
        # TODO
        pass
