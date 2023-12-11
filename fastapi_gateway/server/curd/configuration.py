import uuid
from datetime import datetime
from typing import Union, Optional, List, Dict
from typing_extensions import TypedDict

from pydantic import BaseModel, validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_gateway.server.database import async_session
from fastapi_gateway.server.models import Configuration


async def init_configuration():
    async with async_session() as session:
        await HotSetting.reload_config(session)


class ConfigurationSchema(BaseModel):
    id: uuid.UUID
    key: str
    value: Optional[Union[List[Dict], Dict]] = {}
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = ""
    updated_by: Optional[str] = ""

    @validator("value", pre=True)
    def union_dict_list(cls, v):
        if isinstance(v, list) or isinstance(v, dict):
            return v
        raise ValueError(f"value must a dict or list object, but value '{v}' is {type(v)}")

    class Config:
        orm_mode = True


class ProxyRule(TypedDict):
    path: str
    target: str


class HotSettingSchema(BaseModel):
    PROXY_RULE: List[ProxyRule] = []


class HotSetting(object):
    """
    支持从数据库读取配置
    应以 Settings.attribute 方式来获取值，如 Settings.PROXY_RULE
    """
    # 路由转发规则
    PROXY_RULE: List[ProxyRule] = []

    @classmethod
    async def reload_config(cls, session: AsyncSession):
        await cls.init_config(session)
        # 从数据库重新加载配置
        stmt = select(Configuration)
        configurations = (await session.scalars(stmt)).all()
        obj = {}
        for c in configurations:
            obj[c.key] = c.value
        HotSettingSchema(**obj)
        for c in configurations:
            setattr(cls, c.key, c.value)

    @classmethod
    async def init_config(cls, session: AsyncSession):
        proxy_rule = await cls.get_config(session, "PROXY_RULE")
        if not proxy_rule:
            proxy_rule = Configuration(**{"key": "PROXY_RULE", "value": []})  # noqa
            session.add(proxy_rule)
            await session.commit()

    @classmethod
    async def update_config(cls, session: AsyncSession, key: str, value: Union[dict, list]):
        # 更新配置
        stmt = select(Configuration).where(Configuration.key == key)
        c = (await session.scalars(stmt)).first()
        if c:
            c.value = value

        # 类型校验
        configurations = (await session.scalars(select(Configuration))).all()
        obj = {}
        for c in configurations:
            obj[c.key] = c.value
            if c.key == key:
                obj[c.key] = value
        HotSettingSchema(**obj)
        await session.commit()

        await cls.reload_config(session)

        return c

    @classmethod
    async def get_config(cls, session: AsyncSession, key: str):
        # 获取配置
        stmt = select(Configuration).where(Configuration.key == key)
        c = (await session.scalars(stmt)).first()
        return c

    @classmethod
    async def get_config_list(cls, session: AsyncSession):
        # 获取所有配置
        stmt = select(Configuration)
        configurations = (await session.scalars(stmt)).all()
        return configurations
