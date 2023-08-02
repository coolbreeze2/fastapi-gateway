import uuid
from typing import Optional

import redis.asyncio
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    RedisStrategy
)

from fastapi_gateway.server.curd import SQLAlchemyUserDatabase
from fastapi_gateway.server.depends import get_user_db
from fastapi_gateway.server.models import User
from fastapi_gateway.settings import Settings

SECRET = "SECRET"


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")

cookie_transport = CookieTransport(cookie_max_age=Settings().COOKIE_MAX_AGE, cookie_secure=False, cookie_httponly=False)

redis = redis.asyncio.from_url(Settings().REDIS_URL, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=Settings().JWT_LIFETIME_SECONDS)


bearer_auth_backend = AuthenticationBackend(
    name="bearer",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

cookie_auth_backend = AuthenticationBackend(
    name="cookies",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [bearer_auth_backend, cookie_auth_backend])

current_active_user = fastapi_users.current_user(active=True)
