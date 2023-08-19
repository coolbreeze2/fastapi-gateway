from fastapi_gateway.server.curd.configuration import ConfigurationSchema
from fastapi.testclient import TestClient


def test_get_config(client: TestClient):
    r = client.get("/gate/api/configuration/PROXY_RULE")
    assert r.status_code == 200
    assert r.json().get("key") == "PROXY_RULE"
    ConfigurationSchema(**r.json())


def test_get_configs(client: TestClient):
    r = client.get("/gate/api/configuration/")
    assert r.status_code == 200
    for c in r.json():
        ConfigurationSchema(**c)


def test_update_config(client: TestClient):
    url = "/gate/api/configuration/PROXY_RULE"
    r = client.get(url)
    data = r.json()
    proxy_rule = data.get("value")
    proxy_rule.append({"path": "/test1", "target": "http://www.test.com"})
    r2 = client.patch(url, json=proxy_rule)
    assert r2.status_code == 200
    assert r2.json().get("value") == proxy_rule
