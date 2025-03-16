import logging
from datetime import datetime

import gradio as gr
import numpy as np

from app.interfaces import (
    AudioRecognizerInterface,
    AudioUploaderInterface,
    Page,
    SenderInterface,
)

logger = logging.getLogger("stdout")


class AudioTranscribePage(Page):
    AUDIO_LIMIT = 10**9

    def __init__(
        self,
        uploader: AudioUploaderInterface,
        recognizer: AudioRecognizerInterface,
        sender: SenderInterface,
    ):
        self._audio_uploader = uploader
        self._audo_recognizer = recognizer
        self._sender = sender
        self.theme = None

    @property
    def title(self) -> str:
        return "Расшифровка аудио"

    def _checking_audio(self, audio: np.ndarray):
        logger.info(f"Audio: {audio}")
        if not audio:
            raise ValueError("Укажите аудио для загрузки.")

        if len(audio) >= self.AUDIO_LIMIT:
            raise ValueError("Файл слишком большой!\n Максимальный размер 1 ГБ")

    def _recoginition_audio(self, audio: np.ndarray, speed: bool) -> str:
        logger.info(f"Speed: {speed}")
        gr.Info("Расшифровка аудио файла")
        return self._audo_recognizer.recognize(audio)

    def __do(self, audio: np.ndarray, raw_recipients: str, checkbox_speed: bool):
        # def __do(self, audio_path: str, raw_recipients: str, checkbox_speed: bool):
        start = datetime.now()
        self._checking_audio(audio)
        self._sender.check_input(raw_recipients)

        # Pre-processing
        text_audio = self._recoginition_audio(audio, checkbox_speed)
        if not text_audio:
            raise ValueError("Не удалось расшифровать аудио")

        self._sender.create_message(text_audio)
        self._sender.send(raw_recipients)
        return datetime.now() - start

    # def _conver_file(self, audio_path: str):
    #     logger.info("Conver file to mp3 format")
    #     gr.Info("Конвертация aудио в mp3...")
    #     hash_audio_file = hashlib.md5(audio_path.encode("utf-8")).hexdigest() + ".mp3"
    #     logger.info(f"New hashed audio file: {hash_audio_file}")
    #     self.audio_converter = AudioConverter(audio_path, AudioFiles(hash_audio_file))
    #     self.audio_converter.convert_mp3()
    #     gr.Info("Конвертация завершена!")
    #     return hash_audio_file

    def get_app(self) -> gr.Blocks:
        with gr.Blocks(
            theme=self.theme,
            head="Prompts",
            title="Prompts",
            css="footer {visibility: hidden}",
        ) as app:
            gr.Markdown("# Transcribe audio")

            gr.Markdown(f"### Укажите {self._sender.type}'ы для отправки расшифрованного аудио")
            with gr.Row(equal_height=True, variant="panel"):
                with gr.Column(scale=1):
                    text_title = gr.Textbox(
                        lines=1,
                        interactive=True,
                        show_copy_button=True,
                        info=f"Используйте ';' как разделитель для {self._sender.type}'ов",
                        label=f"Введитe cписок {self._sender.type}'ов:",
                    )
            audio_input = gr.Audio(
                interactive=True,
                label="Выберите аудио для загрузки",
                type="numpy",
                waveform_options=gr.WaveformOptions(
                    waveform_color="#01C6FF",
                    waveform_progress_color="#0066B4",
                ),
            )
            with gr.Row(equal_height=True, variant="panel"):
                checbox_speed = gr.Checkbox(
                    label="Быстро", info="Если выбрано, то будет увеличена скорость загрузки аудио"
                )
                time_text = gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Время Расшифровки:",
                    show_copy_button=True,
                    value="0:00:00.00",
                )
            start_button = gr.Button(
                "Расшифровать аудио",
                size="lg",
                variant="primary",
            )
            start_button.click(
                fn=self.__do, inputs=[audio_input, text_title, checbox_speed], outputs=time_text
            )

        return app
