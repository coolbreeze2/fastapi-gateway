import os

from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles


def init_static(app: FastAPI):
    # gateway 后台管理
    app.mount(
        "/gateway/static",
        StaticFiles(
            directory=os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "assets/dashboard/static"
            )
        ),
        name="gateway dashboard static"
    )

    # swagger 静态文件源使用本服务自身提供，替代 cdn
    applications.get_swagger_ui_html = swagger_monkey_patch
    static_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets/openapi/static')
    app.mount(
        "/openapi/static",
        StaticFiles(directory=static_file_path),
        name="static"
    )


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url="/openapi/static/swagger-ui-bundle.js",
        swagger_css_url="/openapi/static/swagger-ui.css",
    )
