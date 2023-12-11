import uuid
from typing import Optional

import redis.asyncio
from fastapi import Depends, Request, APIRouter, HTTPException, Body
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, exceptions, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    RedisStrategy
)
from fastapi_users.router import ErrorCode
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from starlette import status

from fastapi_gateway.server.curd.user import SQLAlchemyUserDatabase
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

    async def change_password(
        self, user_id, password: str, request: Optional[Request] = None
    ) -> models.UP:
        """
        Reset the password of a user.

        Triggers the on_after_reset_password handler on success.

        :param user_id: The user id to change password.
        :param password: The new password to set.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises InvalidResetPasswordToken: The token is invalid or expired.
        :raises UserInactive: The user is inactive.
        :raises InvalidPasswordException: The password is invalid.
        :return: The user with updated password.
        """
        user = await self.get(user_id)

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user


def get_change_password_router() -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post(
        "/change-password",
        name="change:change_password",
        responses=RESET_PASSWORD_RESPONSES,
    )
    async def change_password(
        request: Request,
        user_id: str = Body(...),
        password: str = Body(...),
        user_manager: UserManager = Depends(get_user_manager),
    ):
        try:
            await user_manager.change_password(user_id, password, request)
        except (
            exceptions.UserNotExists,
            exceptions.UserInactive,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")

cookie_transport = CookieTransport(
    cookie_max_age=Settings().TOKEN_EXPIRED_SECONDS,
    cookie_secure=False,
    cookie_httponly=False
)

redis = redis.asyncio.from_url(Settings().REDIS_URL, decode_responses=True, health_check_interval=30)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=Settings().TOKEN_EXPIRED_SECONDS)


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
