# -*- coding: utf-8 -*-
# @Time    : 2023/5/3 8:29
# @Author  : coodyz
# @File    : settings.py
import json
import os.path
from typing import List, TypedDict

import yaml
from pydantic import BaseSettings


def load_env_from_yaml(path: str = ""):
    if not path:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.yaml")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not config:
        return
    for k, v in config.items():
        if isinstance(v, list) or isinstance(v, dict):
            os.environ[k] = json.dumps(v)
        else:
            os.environ[k] = v


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(asctime)s] %(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["default"], "level": "INFO", "propagate": False},
}


class ProxyRule(TypedDict):
    path: str
    target: str


class Settings(BaseSettings):
    API_DATABASE_CONNECTION_URL: str = ""
    REDIS_URL: str = ""
    JWT_SECRET_KEY: str = "SECRET"
    PROXY_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
    PROXY_RULE: List[ProxyRule] = []
    COOKIE_MAX_AGE: int = 36000
    JWT_LIFETIME_SECONDS: int = 36000


load_env_from_yaml()
