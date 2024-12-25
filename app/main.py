import uvicorn
from fastapi import FastAPI

from app.configs import LogConfig, get_appsettings, get_logger
from app.webui import AudioPage, WebUI

settings = get_appsettings()
logger = get_logger()

app = FastAPI()
app = WebUI(AudioPage()).mount(app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
