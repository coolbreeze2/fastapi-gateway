import os
import uvicorn

from fastapi_gateway.server.app import app
from fastapi_gateway.settings import LOGGING_CONFIG

if __name__ == '__main__':
    port = int(os.getenv("PORT", 80))
    host = os.getenv("HOST", "0.0.0.0")
    log_level = os.getenv("LOG_LEVEL", "info")
    uvicorn.run(app, port=port, host=host, log_level=log_level, log_config=LOGGING_CONFIG)
