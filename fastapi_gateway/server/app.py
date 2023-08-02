import logging
import os
import time

import fastapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import applications, Depends, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response, JSONResponse
from starlette.staticfiles import StaticFiles

from fastapi_gateway.server.router.proxy import reverse_proxy
from fastapi_gateway.settings import load_env_from_yaml, Settings

load_env_from_yaml()

from fastapi_gateway.server.router.users import init_fastapi_users, current_active_user
from fastapi_gateway.server.middleware.casbin import casbin_middleware

S = Settings()

app = fastapi.FastAPI(docs_url="/gateway/docs", openapi_url="/gateway/openapi.json")
init_fastapi_users(app)

logger = logging.getLogger(__file__)


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/")
async def root():
    return RedirectResponse(url='/gateway/dashboard')


@app.get("/gateway/api/health")
async def check_health():
    return {"status": 1, "time": time.time()}


@app.get("/gateway/dashboard")
async def dashboard():
    """dashboard"""
    index_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "dashboard"
    )
    with open(os.path.join(index_dir, 'index.html')) as fh:
        data = fh.read()
    return Response(content=data, media_type="text/html")


@app.exception_handler(HTTPException)
def auth_exception_handler(request: Request, exc: HTTPException):
    """
    Redirect the user to the login page if not logged in
    """
    msg = f"{exc.detail}\n{request.headers}"
    if exc.status_code == 401:
        logger.error(f"触发异常, 请求未认证\n{msg}")
        return RedirectResponse(url='/gateway/dashboard')
    else:
        logger.error(msg)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"{exc.detail}"},
        )


# 后台管理
app.mount(
    "/gateway",
    StaticFiles(
        directory=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "dashboard"
        )
    ),
    name="gatewayDashboard"
)

# swagger 静态文件源使用本服务自身提供，替代 cdn
applications.get_swagger_ui_html = swagger_monkey_patch
static_file_path = os.path.join(os.path.dirname(__file__), 'assets/static')
app.mount(
    "/static",
    StaticFiles(directory=static_file_path),
    name="static"
)

# 路由转发
app.add_api_route(
    path="/{path:path}",
    endpoint=reverse_proxy,
    methods=S.PROXY_METHODS,
    name="gateway proxy",
    include_in_schema=False,
    dependencies=[Depends(casbin_middleware), Depends(current_active_user)],
)

# 跨域允许所有源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
