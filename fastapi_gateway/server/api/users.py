from typing import Optional, Sequence

from fastapi import Depends, FastAPI, APIRouter
from starlette.routing import Route

from fastapi_gateway.server.curd.user import SQLAlchemyUserDatabase
from fastapi_gateway.server.depends import get_user_db
from fastapi_gateway.server.models import User
from fastapi_gateway.server.schemas import UserCreate, UserRead, UserUpdate, UserList
from fastapi_gateway.server.users import bearer_auth_backend, current_active_user, fastapi_users, \
    get_change_password_router


def init_fastapi_users(
    app: FastAPI,
    dependencies: Optional[Sequence[Depends]] = None
):
    app.include_router(
        fastapi_users.get_auth_router(bearer_auth_backend),
        prefix="/gateway/api/auth/jwt",
        tags=["auth"],
        dependencies=dependencies
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/gateway/api/auth",
        tags=["auth"],
        dependencies=dependencies
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/gateway/api/auth",
        tags=["auth"],
        dependencies=dependencies
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/gateway/api/auth",
        tags=["auth"],
        dependencies=dependencies
    )
    app.include_router(
        get_change_password_router(),
        prefix="/gateway/api/auth",
        tags=["auth"],
        dependencies=dependencies
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/gateway/api/users",
        tags=["users"],
        dependencies=dependencies
    )

    router = APIRouter()

    @router.get(
        "/gateway/api/users",
        response_model=UserList,
        name="users:list_users",
    )
    async def get_user_list(
        user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
        page: int = 1,
        limit: int = 10
    ):
        users, total = await user_db.list(page, limit)
        return {"data": users, "total": total}

    @router.get("/gateway/api/authenticated-route")
    async def authenticated_route(user: User = Depends(current_active_user)):
        return {"message": f"Hello {user.email}!"}

    app.include_router(
        router,
        tags=["users"],
        dependencies=dependencies
    )


def get_user_routes(app):
    routes = app.router.routes
    user_routes = []
    for route in routes:
        if isinstance(route, Route) and route.path.startswith("/gateway/api/auth") or route.path.startswith(
            "/gateway/api/users"
        ):
            user_routes.append(route)
    return user_routes
