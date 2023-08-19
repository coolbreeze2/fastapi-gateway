from fastapi import FastAPI, Depends

from .configuration import router as configuration_router
from .health import router as health_router
from .proxy import reverse_proxy
from .root import router as root_router
from .users import init_fastapi_users
from ..middleware.casbin import casbin_middleware
from ..users import current_active_user
from fastapi_gateway.settings import Settings


def init_router(app: FastAPI):
    init_fastapi_users(app)

    app.include_router(
        root_router,
        tags=["root"]
    )

    app.include_router(
        configuration_router,
        prefix="/gateway/api/configuration",
        tags=["configuration"],
        dependencies=[Depends(casbin_middleware), Depends(current_active_user)]
    )

    app.include_router(
        health_router,
        prefix="/gateway/api",
        tags=["health"]
    )

    # 路由转发
    app.add_api_route(
        path="/{path:path}",
        endpoint=reverse_proxy,
        methods=Settings().PROXY_METHODS,
        name="gateway proxy",
        include_in_schema=False,
        dependencies=[Depends(casbin_middleware), Depends(current_active_user)],
    )
