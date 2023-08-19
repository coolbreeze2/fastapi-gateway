from starlette.middleware.cors import CORSMiddleware


def init_cors(app):
    # 跨域允许所有源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
