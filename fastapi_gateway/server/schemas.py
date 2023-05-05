import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator

from fastapi_users import schemas


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.replace(microsecond=0)


class Common(BaseModel):
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID = None
    updated_by: uuid.UUID = None

    _created_at = validator(
        "created_at",
        allow_reuse=True
    )(transform_to_utc_datetime)
    _updated_at = validator(
        "updated_at",
        allow_reuse=True
    )(transform_to_utc_datetime)


class UserRead(Common, schemas.BaseUser[uuid.UUID]):
    username: str
    name: str
    roles: Optional[List[str]]


class UserList(BaseModel):
    data: List[UserRead]
    total: int


class UserCreate(Common, schemas.BaseUserCreate):
    username: str
    name: str


class UserUpdate(Common, schemas.BaseUserUpdate):
    name: str
    roles: Optional[List[str]]
