import uvicorn
from fastapi import FastAPI

from app.backend.api.v1.transcriber import router as transcriber_router
from app.configs import LogConfig, get_appsettings, get_logger

settings = get_appsettings()
logger = get_logger()

app = FastAPI()

# app = WebUI(AudioPage()).mount(app)
# app = WebUI.pages(app, [AudioConverterPage(), AudioUploadPage(), AudioTranscribePage()])

app.include_router(transcriber_router, prefix="/api", tags=["Transcriber"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
