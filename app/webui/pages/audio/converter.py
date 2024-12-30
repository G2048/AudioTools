import logging
from dataclasses import dataclass
from datetime import datetime

import gradio as gr

from app.services import AudioConverter, AudioFile, AudioRecognizer

from ..interfaces import Page

logger = logging.getLogger("stdout")


@dataclass
class AudioFormats:
    MP3 = "mp3"
    WAV = "wav"


class AudioConverterPage(Page):
    AUDIO_LIMIT = 10**9
    FILE_TMP = "/tmp"

    def __init__(self):
        self.audo_recoginition = AudioRecognizer()
        self.theme = None
        self.audio_formats = [AudioFormats.MP3, AudioFormats.WAV]

    @property
    def title(self) -> str:
        return "Конвертация аудио"

    def _checking_audio(self, audio: str):
        logger.info(f"Audio: {audio}")
        if not audio:
            raise ValueError("Укажите аудио для загрузки.")

        if len(audio) >= self.AUDIO_LIMIT:
            raise ValueError("Файл слишком большой!\n Максимальный размер 1 ГБ")

    def __do(self, audio: str, mp3: bool, wav: bool):
        start = datetime.now()
        # Pre-processing
        self._checking_audio(audio)
        if mp3:
            audio_path = self._convert_file(audio, format="mp3", output_path=self.FILE_TMP)
        if wav:
            audio_path = self._convert_file(audio, format="wav", output_path=self.FILE_TMP)

        # Post processing
        return datetime.now() - start

    def _convert_file(self, audio_path: str, format: str = "mp3", output_path: str = "."):
        logger.info(f"Conver file to {format} format")
        gr.Info(f"Конвертация aудио в {format}...")
        # hash_audio_file = hashlib.md5(audio_path.encode("utf-8")).hexdigest() + ".mp3"
        # logger.info(f"New hashed audio file: {hash_audio_file}")

        audio_file = AudioFile(audio_path, output_path)
        self.audio_converter = AudioConverter(file=audio_file)
        self.audio_converter.convert(format=format)

        gr.Info("Конвертация завершена!")
        return audio_file.new_path(format)

    # @staticmethod
    # def __check_box_creator(formats: list[str]):
    #     return [
    #         gr.Checkbox(label=format, info="Аудио будет преобразовано в %s" % format) for format in formats
    #     ]

    def get_app(self) -> gr.Blocks:
        with gr.Blocks(
            theme=self.theme,
            head="Prompts",
            title="Prompts",
            css="footer {visibility: hidden}",
        ) as app:
            gr.Markdown("# Converting audio")

            gr.Markdown("### Выберите формат аудио для конвертации")
            with gr.Row(equal_height=True, variant="panel"):
                # check_boxs = self.__check_box_creator(self.audio_formats)
                checkbox_mp3 = gr.Checkbox(label="mp3", info="Аудио будет преобразовано в mp3")
                checkbox_wav = gr.Checkbox(label="wav", info="Аудио будет преобразовано в wav")

            audio_input = gr.Audio(
                interactive=True,
                label="Выберите аудио для загрузки",
                type="filepath",
                waveform_options=gr.WaveformOptions(
                    waveform_color="#01C6FF",
                    waveform_progress_color="#0066B4",
                ),
            )
            with gr.Row(equal_height=True, variant="panel"):
                time_text = gr.Textbox(
                    lines=1,
                    interactive=False,
                    label="Время Конвертации:",
                    show_copy_button=True,
                    value="0:00:00.00",
                )
            start_button = gr.Button(
                "Конвертация аудио",
                size="lg",
                variant="primary",
            )

            start_button.click(
                fn=self.__do,
                inputs=[audio_input, checkbox_mp3, checkbox_wav],
                outputs=time_text,
            )

        return app
