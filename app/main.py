import uvicorn
from fastapi import FastAPI

from app.backend.api.v1.transcriber import router as transcriber_router
from app.configs import LogConfig, get_appsettings, get_logger
from app.webui import AudioConverterPage, AudioTranscribePage, AudioUploadPage, WebUI

settings = get_appsettings()
logger = get_logger()

app = FastAPI()

app.include_router(transcriber_router, prefix="/api", tags=["Transcriber"])
app = WebUI.pages(app, [AudioConverterPage(), AudioUploadPage(), AudioTranscribePage()])


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
