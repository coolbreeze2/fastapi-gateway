import os

from fastapi_users.password import PasswordHelper
from typing import Dict, Any, Optional, Type, Generic, List, Tuple

from fastapi_users.models import UP, ID
import sqlalchemy as sa
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from casbin import persist, Model

from .database import async_session
from .models import User, CasbinRule

casbin_model = Model()
casbin_model.load_model(os.path.join(os.path.dirname(__file__), "rbac_model.conf"))


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


async def create_init_rules():
    adapter = Adapter(model=casbin_model)
    rules = [
        ["*", "/login", "*"],
        ["admin", "*", "*"]
    ]
    await adapter.load_policy()
    await adapter.add_policies("p", "p", rules)


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


class Filter:
    ptype = []
    v0 = []
    v1 = []
    v2 = []
    v3 = []
    v4 = []
    v5 = []


class Adapter(persist.Adapter):
    """the interface for Casbin adapters."""

    def __init__(self, filtered=False, model=None):
        self._db_class = CasbinRule
        self._filtered = filtered
        self.model = model

    async def load_policy(self, model=None):
        """loads all policy rules from the storage."""
        model = model or self.model
        async with async_session() as session:
            statement = select(self._db_class)
            lines = (await session.scalars(statement)).all()
            for line in lines:
                persist.load_policy_line(str(line), model)

    def is_filtered(self):
        return self._filtered

    async def load_filtered_policy(self, model, _filter) -> None:
        """loads all policy rules from the storage."""
        async with async_session() as session:
            query = await session.query(self._db_class)
            filters = await self.filter_query(query, _filter)
            filters = await filters.all()

            for line in filters:
                persist.load_policy_line(str(line), model)
            self._filtered = True

    async def filter_query(self, query, _filter):
        for attr in ("ptype", "v0", "v1", "v2", "v3", "v4", "v5"):
            if len(getattr(_filter, attr)) > 0:
                query = await query.filter(
                    getattr(self._db_class, attr).in_(getattr(_filter, attr))
                )
        return await query.order_by(self._db_class.id)

    async def _save_policy_line(self, session, ptype, rule, commit=True):
        line = self._db_class(ptype=ptype)
        for i, v in enumerate(rule):
            setattr(line, "v{}".format(i), v)
        session.add(line)
        if commit:
            await session.commit()

    async def save_policy(self, model=None):
        """saves all policy rules to the storage."""
        model = model or self.model
        async with async_session() as session:
            # delete all
            await session.execute(
                sa.delete(self._db_class)
            )
            await session.commit()

            # recreate
            for sec in ["p", "g"]:
                if sec not in model.model.keys():
                    continue
                for ptype, ast in model.model[sec].items():
                    for rule in ast.policy:
                        await self._save_policy_line(session, ptype, rule, commit=False)
            await session.commit()
            return True

    async def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        async with async_session() as session:
            if not self.model.has_policy(sec, ptype, rule):
                await self._save_policy_line(session, ptype, rule)
                return True
        return False

    async def add_policies(self, sec, ptype, rules):
        """adds a policy rules to the storage."""
        async with async_session() as session:
            for rule in rules:
                if not self.model.has_policy(sec, ptype, rule):
                    await self._save_policy_line(session, ptype, rule, commit=False)
            await session.commit()

    async def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        async with async_session() as session:
            query = await session.query(self._db_class)
            query = await query.filter(self._db_class.ptype == ptype)
            for i, v in enumerate(rule):
                query = await query.filter(getattr(self._db_class, "v{}".format(i)) == v)
            r = await query.delete()

            return True if r > 0 else False

    async def remove_policies(self, sec, ptype, rules):
        """remove policy rules from the storage."""
        if not rules:
            return
        async with async_session() as session:
            query = await session.query(self._db_class).filter(self._db_class.ptype == ptype)
            rules = zip(*rules)
            for i, rule in enumerate(rules):
                query = await query.filter(
                    or_(getattr(self._db_class, "v{}".format(i)) == v for v in rule)
                )
            await query.delete()

    async def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        async with async_session() as session:
            query = await session.query(self._db_class).filter(self._db_class.ptype == ptype)

            if not (0 <= field_index <= 5):
                return False
            if not (1 <= field_index + len(field_values) <= 6):
                return False
            for i, v in enumerate(field_values):
                if v != "":
                    v_value = getattr(self._db_class, "v{}".format(field_index + i))
                    query = await query.filter(v_value == v)
            r = await query.delete()

        return True if r > 0 else False

    async def update_policy(
            self, sec: str, ptype: str, old_rule: [str], new_rule: [str]
    ) -> None:
        """
        Update the old_rule with the new_rule in the database (storage).

        :param sec: section type
        :param ptype: policy type
        :param old_rule: the old rule that needs to be modified
        :param new_rule: the new rule to replace the old rule

        :return: None
        """
        async with async_session() as session:
            query = await session.query(self._db_class).filter(self._db_class.ptype == ptype)

            # locate the old rule
            for index, value in enumerate(old_rule):
                v_value = getattr(self._db_class, "v{}".format(index))
                query = await query.filter(v_value == value)

            # need the length of the longest_rule to perform overwrite
            longest_rule = old_rule if len(old_rule) > len(new_rule) else new_rule
            old_rule_line = await query.one()

            # overwrite the old rule with the new rule
            for index in range(len(longest_rule)):
                if index < len(new_rule):
                    exec(f"old_rule_line.v{index} = new_rule[{index}]")
                else:
                    exec(f"old_rule_line.v{index} = None")

    async def update_policies(
            self,
            sec: str,
            ptype: str,
            old_rules: [
                [str],
            ],
            new_rules: [
                [str],
            ],
    ) -> None:
        """
        Update the old_rules with the new_rules in the database (storage).

        :param sec: section type
        :param ptype: policy type
        :param old_rules: the old rules that need to be modified
        :param new_rules: the new rules to replace the old rules

        :return: None
        """
        for i in range(len(old_rules)):
            await self.update_policy(sec, ptype, old_rules[i], new_rules[i])

    async def update_filtered_policies(
            self, sec, ptype, new_rules: [[str]], field_index, *field_values
    ) -> [[str]]:
        """update_filtered_policies updates all the policies on the basis of the filter."""

        _filter = Filter()
        _filter.ptype = ptype

        # Creating Filter from the field_index & field_values provided
        for i in range(len(field_values)):
            if field_index <= i < field_index + len(field_values):
                setattr(_filter, f"v{i}", field_values[i - field_index])
            else:
                break

        await self._update_filtered_policies(new_rules, _filter)

    async def _update_filtered_policies(self, new_rules, _filter) -> [[str]]:
        """_update_filtered_policies updates all the policies on the basis of the filter."""

        # Load old policies
        async with async_session() as session:
            query = await session.query(self._db_class).filter(
                self._db_class.ptype == _filter.ptype
            )
            old_rules = await self.filter_query(query, _filter).all()

            # Delete old policies

            await self.remove_policies("p", _filter.ptype, old_rules)

            # Insert new policies

            await self.add_policies("p", _filter.ptype, new_rules)

            # return deleted rules

            return old_rules
