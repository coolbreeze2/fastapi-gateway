import asyncio
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi_gateway.server.app import app

from fastapi_gateway.settings import Settings


@pytest.fixture
def env_file_path():
    return os.path.join(os.path.dirname(__file__), ".env.test.yaml")


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(Settings().DATABASE_CONNECTION_URL, pool_pre_ping=True)
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
