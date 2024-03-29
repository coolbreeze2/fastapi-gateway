# -*- coding: utf-8 -*-
# @Time    : 2023/5/3 8:29
# @Author  : coodyz
# @File    : settings.py
import json
import os.path
from typing import List

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


class Settings(BaseSettings):
    # postgres 数据库地址
    DATABASE_CONNECTION_URL: str = ""
    # Redis 地址
    REDIS_URL: str = ""
    # 支持转发的 http method
    PROXY_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
    # token 有效期
    TOKEN_EXPIRED_SECONDS: int = 36000
    # 鉴权排除的路径 TODO: 考虑写入 casbin rule policy
    EXCLUDE_AUTH_PATHS: List[str] = ["/", "/gateway/docs", "/gateway/openapi.json", "/gateway/auth/jwt/login"]


load_env_from_yaml()
