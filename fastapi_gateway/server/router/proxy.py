import re
import time
import logging
from typing import List
from urllib.parse import urlparse
from urllib.parse import urljoin

import httpx
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.exceptions import HTTPException
from starlette.background import BackgroundTask

from fastapi_gateway.settings import Settings, ProxyRule

logger = logging.getLogger(__file__)

client = httpx.AsyncClient()


def get_proxy_url(path: str, rule: List[ProxyRule]) -> str:
    """
    获取指定路由下的目的路由
    """
    # 根据路由路径字符长度排序，优先匹配字符长的路由
    score = -1
    match_route = None
    for route in rule:
        if re.search(f"^{route['path']}", path):
            path_length = len(route['path'])
            if path_length > score:
                score = path_length
                match_route = route
    if not match_route:
        return ""
    return urljoin(match_route["target"], path[score:])


async def reverse_proxy(request: Request):
    """路由转发"""
    logger.info(f"请求正在转发: {request.url.path}")
    request.scope.update()
    request_path = request.url.path
    s = Settings()
    target_url = get_proxy_url(request_path, s.PROXY_RULE)
    if not target_url:
        raise HTTPException(status_code=404, detail=f"Proxy 404 Not Found")
    headers = request.headers.raw
    domain = urlparse(target_url).netloc
    headers[0] = (b'host', domain.encode())
    rp_req = client.build_request(
        request.method,
        target_url,
        headers=headers,
        content=await request.body()
    )
    s_time = time.time()
    rp_resp = await client.send(rp_req, stream=True)
    logger.info(f"{time.time() - s_time}s proxy to '{rp_req.url}', resp: {rp_resp}\n{request.headers}")
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )
