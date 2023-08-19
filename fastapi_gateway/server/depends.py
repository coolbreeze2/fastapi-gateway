from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from fastapi_gateway.server.curd.user import SQLAlchemyUserDatabase
from fastapi_gateway.server.database import get_async_session
from fastapi_gateway.server.models import User

API_KEY_NAME = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def check_api_key(key: str = Depends(api_key_header)):
    if key:
        return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You didn't pass the api key in the header! Header: x-api-key",
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
