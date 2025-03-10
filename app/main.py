import uvicorn
from fastapi import FastAPI

from app.adapters import EmailSenderAdapter
from app.configs import LogConfig, get_appsettings, get_logger
from app.configs.settings import get_email_settings
from app.services import AudioRecognizer, AudioUploader
from app.webui import AudioConverterPage, AudioTranscribePage, AudioUploadPage, WebUI

logger = get_logger()
settings = get_appsettings()
email_settings = get_email_settings()

logger.debug(f"Email settings: {email_settings}")

app = FastAPI()

# app = WebUI(AudioPage()).mount(app)
app = WebUI.pages(
    app,
    [
        AudioConverterPage(),
        AudioUploadPage(),
        AudioTranscribePage(
            AudioUploader(),
            AudioRecognizer(),
            # AwsAudioUploader(),
            # SberSpeechRecognizer(),
            EmailSenderAdapter(email_settings),
        ),
    ],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
