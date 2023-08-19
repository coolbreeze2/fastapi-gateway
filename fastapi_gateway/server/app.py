import fastapi

from fastapi_gateway.server.api.api import init_router
from fastapi_gateway.server.api.static import init_static
from fastapi_gateway.server.events.handler import init_event
from fastapi_gateway.server.middleware.init import init_cors
from fastapi_gateway.settings import load_env_from_yaml
from fastapi_gateway.server.exceptions.handlers import init_exception_handlers


def init_app():
    load_env_from_yaml()
    _app = fastapi.FastAPI(docs_url="/gateway/docs", openapi_url="/gateway/openapi.json")
    init_event(_app)
    init_exception_handlers(_app)
    init_static(_app)
    init_router(_app)
    init_cors(_app)
    return _app


app = init_app()
