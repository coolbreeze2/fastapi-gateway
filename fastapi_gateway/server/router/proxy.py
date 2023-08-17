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
    # TODO: 使用前缀树匹配算法
    # TODO: 支持从数据库加载路由规则，并支持热加载
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
    if match_route["target"][-1] == '/':
        target_url = match_route["target"] + path[score + 1:]
    else:
        target_url = urljoin(match_route["target"], path[score:])
    return target_url


async def reverse_proxy(request: Request):
    """路由转发"""
    logger.info(f"request is proxying: {request.url.path}")
    request.scope.update()
    request_path = request.url.path
    s = Settings()
    target_url = get_proxy_url(request_path, s.PROXY_RULE)
    logger.info(f"request '{request.url.path}' proxy to {target_url}")
    if not target_url:
        raise HTTPException(status_code=404, detail=f"Proxy '{request_path}' 404 Not Found")
    headers = request.headers.raw
    domain = urlparse(target_url).netloc
    headers[0] = (b'host', domain.encode())
    request_body = await request.body()
    rp_req = client.build_request(
        request.method,
        target_url,
        headers=headers,
        params=request.query_params,
        content=request_body
    )
    s_time = time.time()
    rp_resp = await client.send(rp_req, stream=True)
    logger.info(f"{time.time() - s_time}s proxy to '{rp_req.url}'")
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "headers": request.headers.items(),
        "cookies": request.cookies.items(),
        "params": request.query_params.items(),
        "body": request_body
    }
    response_info = {
        "url": str(rp_resp.url),
        "headers": rp_resp.headers.items(),
        "cookies": rp_resp.cookies.items(),
        "body": request_body,
        "request": rp_resp.request,
    }
    proxy_info = {
        "request": request_info,
        "response": response_info
    }
    logger.info(proxy_info)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )
