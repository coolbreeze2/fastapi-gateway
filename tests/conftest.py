import asyncio
import os

import pytest


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
