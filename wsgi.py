import uvicorn

from fastapi_gateway.server.app import app
from fastapi_gateway.settings import LOGGING_CONFIG

if __name__ == '__main__':
    uvicorn.run(app, port=80, host="0.0.0.0", log_level="info", log_config=LOGGING_CONFIG)
