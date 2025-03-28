import uvicorn
from fastapi import FastAPI, status

# from app.adapters import AudioAwsUploader, EmailSenderAdapter, WhisperRecognizer
# from app.webui import AudioConverterPage, AudioTranscribePage, AudioUploadPage, WebUI
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


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(routers_v1.login)
app.include_router(routers_v1.audio)

# app = WebUI(AudioPage()).mount(app)
# app = WebUI.pages(
#     app,
#     [
#         AudioConverterPage(),
#         AudioUploadPage(),
#         AudioTranscribePage(
#             AudioAwsUploader(),
#             WhisperRecognizer(),
#             # AwsAudioUploader(),
#             # SberSpeechRecognizer(),
#             EmailSenderAdapter(),
#         ),
#     ],
# )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
