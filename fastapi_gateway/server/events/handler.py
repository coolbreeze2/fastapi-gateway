from fastapi import FastAPI

from fastapi_gateway.server.curd.casbin import create_init_rules
from fastapi_gateway.server.curd.configuration import init_configuration
from fastapi_gateway.server.curd.user import create_admin_user
from fastapi_gateway.server.database import create_db_and_tables


def init_event(app: FastAPI):
    @app.on_event("startup")
    async def on_startup():
        # Not needed if you setup a migration system like Alembic
        await init_configuration()
        await create_db_and_tables()
        await create_admin_user()
        await create_init_rules()
