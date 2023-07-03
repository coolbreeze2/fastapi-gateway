import logging
import os
import time
from urllib.parse import urlparse

import fastapi
import httpx
from fastapi import Depends, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse, RedirectResponse, Response, JSONResponse
from starlette.background import BackgroundTask
from starlette.staticfiles import StaticFiles

from fastapi_gateway.settings import load_env_from_yaml, Settings

load_env_from_yaml()

from fastapi_gateway.server.router.users import init_fastapi_users, current_active_user
from fastapi_gateway.server.middleware.casbin import casbin_middleware

S = Settings()

app = fastapi.FastAPI()
init_fastapi_users(app)

client = httpx.AsyncClient(base_url=S.SERVICE_URL)

logger = logging.getLogger(__file__)


@app.get("/api/health")
async def check_health():
    return {"status": 1, "time": time.time()}


@app.get("/dashboard")
async def main():
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
        return RedirectResponse(url='/dashboard')
    else:
        logger.error(msg)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"{exc.detail}"},
        )


async def _reverse_proxy(request: Request):
    target_url = request.url.path
    url = httpx.URL(path=target_url,
                    query=request.url.query.encode("utf-8"))
    request.scope.update()
    headers = request.headers.raw

    domain = urlparse(S.SERVICE_URL).netloc
    headers[0] = (b'host', domain.encode())
    rp_req = client.build_request(request.method,
                                  url,
                                  headers=headers,
                                  content=await request.body())
    s_time = time.time()
    rp_resp = await client.send(rp_req, stream=True)
    logger.info(f"{time.time() - s_time}s proxy '{rp_req.url}', resp: {rp_resp}\n{request.headers}")
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


app.mount(
    "/dashboard",
    StaticFiles(
        directory=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "dashboard"
        )
    ),
    name="dashboard"
)

app.add_api_route(
    path="/{path:path}",
    endpoint=_reverse_proxy,
    methods=S.PROXY_METHODS,
    name="api gateway",
    include_in_schema=True,
    dependencies=[Depends(casbin_middleware), Depends(current_active_user)]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
