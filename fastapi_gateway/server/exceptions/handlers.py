import logging

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

logger = logging.getLogger()


def init_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    def auth_exception_handler(request: Request, exc: HTTPException):
        """
        Redirect the user to the login page if not logged in
        """
        msg = f"{exc.detail}\n{request.headers}"
        if exc.status_code == 401:
            logger.error(f"触发异常, 请求未认证\n{msg}")
            return RedirectResponse(url='/gateway/dashboard')
        else:
            logger.error(msg)
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": f"{exc.detail}"},
            )
