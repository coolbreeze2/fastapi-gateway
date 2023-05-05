# -*- coding: utf-8 -*-
# @Time    : 2023/5/3 8:40
# @Author  : coodyz
# @File    : test_settings.py
import os

from fastapi_gateway.settings import load_env_from_yaml, Settings


class TestConfig:
    API_DATABASE_CONNECTION_URL = "postgresql+asyncpg://test:test@postgresql:6432/test"
    JWT_SECRET_KEY = "SECRET"
    PROXY_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
    SERVICE_URL = "http://test-server.com"


def test_load_env_from_yaml(env_file_path):
    load_env_from_yaml(env_file_path)
    for k, v in TestConfig().__dict__.items():
        assert v == os.environ.get(k)


def test_settings(env_file_path):
    load_env_from_yaml(env_file_path)
    s = Settings()
    for k, v in TestConfig().__dict__.items():
        assert v == getattr(s, k)
