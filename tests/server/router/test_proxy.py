from typing import List

import pytest

from fastapi_gateway.server.curd.configuration import ProxyRule
from fastapi_gateway.server.router.proxy import get_proxy_url


@pytest.mark.parametrize(
    "rule,path,expected",
    [
        ([{"path": "/example", "target": "http://www.example.com"}], "/example/api", "http://www.example.com/api"),
        (
            [{"path": "/example", "target": "http://www.example.com"}],
            "/example/api?x=1",
            "http://www.example.com/api?x=1"
        ),
        ([{"path": "/example", "target": "http://www.example.com"}], "/example", "http://www.example.com"),
        (
            [
                {"path": "/example", "target": "http://www.example.com"},
                {"path": "/example/path", "target": "http://www.example2.com/path"}
            ],
            "/example/path",
            "http://www.example2.com/path"
        ),
    ]
)
def test_get_proxy_url(rule: List[ProxyRule], path: str, expected: str):
    result = get_proxy_url(path, rule)
    assert result == expected
