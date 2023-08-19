import pytest
from pydantic import ValidationError

from fastapi_gateway.server.curd.configuration import HotSetting


class TestHotSetting(object):
    async def test_init_config(self, session):
        await HotSetting.reload_config(session)
        print(HotSetting.PROXY_RULE)

    async def test_update_config(self, session):
        key = "PROXY_RULE"
        value = [
            {"path": "/example", "target": "http://www.example.com"},
            {"path": "/example/path", "target": "http://www.example2.com/path"}
        ]
        await HotSetting.update_config(session=session, key=key, value=value)
        await HotSetting.reload_config(session=session)
        assert HotSetting.PROXY_RULE == value

        value2 = "xyz"
        with pytest.raises(ValidationError, match="value is not a valid list"):
            await HotSetting.update_config(session=session, key=key, value=value2)  # noqa

    async def test_get_config(self, session):
        key = "PROXY_RULE"
        c = await HotSetting.get_config(session, key=key)
        assert c.key == key

        fake_key = "FAKE_KEY"
        c2 = await HotSetting.get_config(session, key=fake_key)
        assert c2 is None

    async def test_get_config_list(self, session):
        configs = await HotSetting.get_config_list(session=session)
        assert isinstance(configs, list)
