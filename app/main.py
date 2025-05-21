import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import routers as routers_v1
from app.configs import LogConfig, get_app_settings, get_logger

logger = get_logger()
settings = get_app_settings()


app = FastAPI(
    title=settings.appname.capitalize(),
    description=settings.appname,
    version=settings.appversion,
    debug=settings.debug,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(routers_v1.login)
app.include_router(routers_v1.audio)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8080, reload=False, log_config=LogConfig
    )
