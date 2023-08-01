from typing import List

import pytest

from fastapi_gateway.server.router.proxy import get_proxy_url
from fastapi_gateway.settings import ProxyRule


@pytest.mark.parametrize(
    "rule,path,expected",
    [
        ([{"path": "/example", "target": "http://www.example.com"}], "/example/api", "http://www.example.com/api"),
        ([{"path": "/example", "target": "http://www.example.com"}], "/example", "http://www.example.com")
    ]
)
def test_get_proxy_url(rule: List[ProxyRule], path: str, expected: str):
    assert get_proxy_url(path, rule) == expected
