import uvicorn
from fastapi import FastAPI, status

from app.adapters import AudioAwsUploader, EmailSenderAdapter, LocalNeuralAudioRecognizer
from app.configs import LogConfig, get_app_settings, get_email_settings, get_logger
from app.webui import AudioConverterPage, AudioTranscribePage, AudioUploadPage, WebUI

logger = get_logger()
settings = get_app_settings()
email_settings = get_email_settings()

logger.debug(f"Email settings: {email_settings}")

app = FastAPI(
    title=settings.appname.capitalize(),
    description=settings.appname,
    version=settings.appversion,
    debug=settings.debug,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "ok"}


# app = WebUI(AudioPage()).mount(app)
app = WebUI.pages(
    app,
    [
        AudioConverterPage(),
        AudioUploadPage(),
        AudioTranscribePage(
            AudioAwsUploader(),
            LocalNeuralAudioRecognizer(),
            # AwsAudioUploader(),
            # SberSpeechRecognizer(),
            EmailSenderAdapter(email_settings),
        ),
    ],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True, log_config=LogConfig)
