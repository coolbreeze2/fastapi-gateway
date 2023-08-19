from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_gateway.server.curd.configuration import HotSetting, ConfigurationSchema
from fastapi_gateway.server.database import get_async_session

router = APIRouter()


@router.get("/{key}", response_model=ConfigurationSchema)
async def read_config(*, session: AsyncSession = Depends(get_async_session), key: str):
    c = await HotSetting.get_config(session=session, key=key)
    if not c:
        raise HTTPException(status_code=404, detail=f"config {key} not found")
    return c


@router.get("/", response_model=List[ConfigurationSchema])
async def read_configs(session: AsyncSession = Depends(get_async_session)):
    configs = await HotSetting.get_config_list(session)
    return configs


@router.patch("/{key}", response_model=ConfigurationSchema)
async def update_config(*, session: AsyncSession = Depends(get_async_session), key: str, value: Union[list, dict]):
    c = await HotSetting.update_config(session=session, key=key, value=value)
    if not c:
        raise HTTPException(status_code=404, detail=f"config {key} not found")
    return c
