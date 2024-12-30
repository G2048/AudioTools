import logging
import os

import gradio as gr
import numpy as np

from app.configs.settings import get_email_settings
from app.services import AudioConverter, AudioRecognizer, AudioUploader, EmailSender

from ..interfaces import Page

logger = logging.getLogger("stdout")
email_settings = get_email_settings()
logger.debug(f"Email settings: {email_settings}")


class AudioUploadPage(Page):
    AUDIO_LIMIT = 10**9

    def __init__(self):
        self.audo_recoginition = AudioRecognizer()
        self.audio_uploader = AudioUploader()
        self.email_sender = EmailSender(email_settings)
        self.theme = None

    @property
    def title(self) -> str:
        return "Загрузка аудио в облако"

    def _checking_audio(self, audio_path: str):
        logger.info(f"Audio: {audio_path}")
        if not audio_path:
            raise ValueError("Укажите аудио для загрузки.")

        if os.path.getsize(audio_path) >= self.AUDIO_LIMIT:
            raise ValueError("Файл слишком большой!\n Максимальный размер 1 ГБ")

    def _recoginition_audio(self, audio: np.ndarray, speed: bool) -> str:
        logger.info(f"Speed: {speed}")
        gr.Info(f"Расшифровка {audio} файла")
        return self.audo_recoginition.execute(audio)

    def _conver_file(self, audio_path: str):
        logger.info("Conver file to mp3 format")
        gr.Info("Конвертация aудио в mp3...")
        # hash_audio_file = hashlib.md5(audio_path.encode("utf-8")).hexdigest() + ".mp3"
        logger.info(f"New hashed audio file: {hash_audio_file}")
        self.audio_converter = AudioConverter(audio_path, AudioFiles(hash_audio_file))
        self.audio_converter.convert_mp3()
        gr.Info("Конвертация завершена!")
        return hash_audio_file

    def _upload_file(self, audio: str, speed: bool):
        logger.info("Uploading file...")
        audio_name = audio.split("/")[-1]
        logger.info(f"Uploading audio file: {audio_name}")
        gr.Info(f"Загрузка {audio_name} файла")

        # TODO: release speed option
        if speed:
            self.audio_uploader.execute(audio_name)
        else:
            self.audio_uploader.execute(audio_name)
        gr.Info(f"Файл {audio_name} загружен")
        os.remove(audio)
        logger.info(f"File {audio_name} removed")

    def __do(self, audio_path: str, raw_emails: str, checkbox_speed: bool):
        start = datetime.now()
        self._checking_audio(audio_path)

        # Pre-processing
        # new_file_name = self._conver_file(audio_path)
        return datetime.now() - start

    def get_app(self) -> gr.Blocks:
        with gr.Blocks(
            theme=self.theme,
            head="Prompts",
            title="Prompts",
            css="footer {visibility: hidden}",
        ) as app:
            gr.Markdown("# Upload audio to Cloud Storage")

            audio_input = gr.Audio(
                interactive=True,
                label="Выберите аудио для загрузки",
                type="numpy",
                waveform_options=gr.WaveformOptions(
                    waveform_color="#01C6FF",
                    waveform_progress_color="#0066B4",
                    # skip_length=2,
                    # show_controls=False,
                ),
            )
            with gr.Row(equal_height=True, variant="panel"):
                gr.Radio(
                    ["mp3", "wav"], label="Форматы аудио", info="Выберите формат аудио для загрузки в облако"
                )
                # checbox_mp3 = gr.Checkbox(label="mp3", info="Аудио будет преобразовано в mp3")
                # checbox_wav = gr.Checkbox(label="wav", info="Аудио будет преобразовано в wav")
            with gr.Row(equal_height=True, variant="panel"):
                checbox_speed = gr.Checkbox(
                    label="Быстро", info="Если выбрано, то будет увеличена скорость загрузки аудио"
                )
                time_text = gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Время Загрузки:",
                    show_copy_button=True,
                    value="0:00:00.00",
                )
            start_button = gr.Button(
                "Отправить аудио",
                size="lg",
                variant="primary",
            )
            start_button.click(fn=self.__do, inputs=[audio_input, checbox_speed], outputs=time_text)

            # audio_input.change(
            #     inputs=audio_input, outputs=text_output, fn=lambda x: f"Audio changed to {x}"
            # )

        return app
