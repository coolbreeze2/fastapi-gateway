from typing import List

import casbin
from casbin.enforcer import Enforcer
from fastapi import Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from fastapi_gateway.server.curd import Adapter, casbin_model
from fastapi_gateway.server.models import User
from fastapi_gateway.server.users import current_active_user
from fastapi_gateway.settings import Settings


class CasbinMiddleware:
    """
    Middleware for Casbin
    """

    def __init__(
        self,
        enforcer: Enforcer,
        exclude_users: List[str] = None
    ) -> None:
        """
        Configure Casbin Middleware

        :param enforcer: Casbin Enforcer, must be initialized before FastAPI start.
        :param exclude_users
        """
        self.enforcer = enforcer
        self.exclude_users = exclude_users

    async def __call__(self, request: Request, user: User = Depends(current_active_user)) -> None:
        if self._enforce(request, user) or request.method == "OPTIONS":
            return
        else:
            status_code = HTTP_403_FORBIDDEN
            raise HTTPException(status_code=status_code)

    def _enforce(self, request: Request, user: User) -> bool:
        """
        Enforce a request

        :param user: user will be sent to enforcer
        :param request: ASGI Request
        :return: Enforce Result
        """
        path = request.url.path
        method = request.method
        if self.exclude_users and user.username in self.exclude_users:
            return True
        exclude_auth_paths = Settings().EXCLUDE_AUTH_PATHS
        if exclude_auth_paths and path in exclude_auth_paths:
            return True
        if not user:
            raise RuntimeError("Casbin Middleware must work with an Authentication Middleware")

        assert isinstance(user, User)

        user = user.username if user else 'anonymous'

        return self.enforcer.enforce(user, path, method)


adapter = Adapter(model=casbin_model)
enforcer = casbin.Enforcer(casbin_model, adapter)
casbin_middleware = CasbinMiddleware(
    enforcer=enforcer
)
