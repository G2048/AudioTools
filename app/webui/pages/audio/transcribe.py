import logging
import re
from datetime import datetime

import gradio as gr
import numpy as np

from app.configs.settings import get_email_settings
from app.services import AudioRecognizer, Email, EmailSender

from ..interfaces import Page

logger = logging.getLogger("stdout")
email_settings = get_email_settings()
logger.debug(f"Email settings: {email_settings}")


class AudioTranscribePage(Page):
    AUDIO_LIMIT = 10**9
    re_email = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    email_message = """Здравствуйте!
    \nВы получили аудио запрос на расшифровку в моей группе.
    \nЕсли вы получили это сообщение по ошибке, то сообщите мне по email или в чате.
    """
    email_message_template = """Здравствуйте!
    \nВаша расшифровка аудио запроса:
    \n%s
    \nЕсли вы получили это сообщение по ошибке, то сообщите мне по email или в чате.
    """

    def __init__(self):
        self.audo_recoginition = AudioRecognizer()
        self.email_sender = EmailSender(email_settings)
        self.theme = None

    @property
    def title(self) -> str:
        return "Расшифровка аудио"

    # Test emails:
    # go@yandex.ru;print; urea@gmai l.com, so@ydex.ru;print; urea@gmail.com
    def __filter_emails(self, emails: str) -> tuple:
        return tuple(filter(self.re_email.findall, emails.split(";")))

    def _send_email(self, emails: tuple[str], text: str):
        gr.Info(f"Отправлено уведомление для {emails} пользователей")
        logger.info(f"Sending emails to {emails}")

        g_emails = (Email(email, text) for email in emails)
        self.email_sender.execute(g_emails)
        return emails

    def _checking_email(self, raw_emails: str):
        logger.debug(f"Doing with {raw_emails}")
        emails = self.__filter_emails(raw_emails)
        if not emails:
            raise ValueError(
                "Пожалуйста, укажите хотя бы один email.\n Используйте ';' как разделитель для email'ов"
            )
        return emails

    def _checking_audio(self, audio: np.ndarray):
        logger.info(f"Audio: {audio}")
        if not audio:
            raise ValueError("Укажите аудио для загрузки.")

        if len(audio) >= self.AUDIO_LIMIT:
            raise ValueError("Файл слишком большой!\n Максимальный размер 1 ГБ")

    def __do(self, audio: np.ndarray, raw_emails: str, checkbox_speed: bool):
        # def __do(self, audio_path: str, raw_emails: str, checkbox_speed: bool):
        start = datetime.now()
        self._checking_audio(audio)
        emails = self._checking_email(raw_emails)

        # Pre-processing
        text_audio = self._recoginition_audio(audio, checkbox_speed)
        if not text_audio:
            raise ValueError("Не удалось расшифровать аудио")

        # Post processing
        # I don't know whether uploading file to aws
        self._send_email(emails, self.email_message_template % text_audio)
        return datetime.now() - start

    def _recoginition_audio(self, audio: np.ndarray, speed: bool) -> str:
        logger.info(f"Speed: {speed}")
        gr.Info("Расшифровка аудио файла")
        return self.audo_recoginition.execute(audio)

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
            gr.Markdown("# Trasncribe audio")

            gr.Markdown("### Укажите email'ы для отправки расшифрованного аудио")
            with gr.Row(equal_height=True, variant="panel"):
                with gr.Column(scale=1):
                    text_emails = gr.Textbox(
                        lines=1,
                        interactive=True,
                        show_copy_button=True,
                        info="Используйте ';' как разделитель для email'ов",
                        label="Введитe cписок email'ов:",
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
                fn=self.__do, inputs=[audio_input, text_emails, checbox_speed], outputs=time_text
            )

        return app
