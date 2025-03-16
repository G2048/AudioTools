import logging
import re

from app.configs import get_email_settings
from app.drivers import Email, EmailSender
from app.interfaces import SenderInterface

logger = logging.getLogger("stdout")
email_settings = get_email_settings()
logger.debug(f"Email settings: {email_settings}")


class EmailSenderAdapter(SenderInterface):
    re_email = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    email_message_template = """Здравствуйте!
    \nВаша расшифровка аудио запроса:
    \n%s
    \nЕсли вы получили это сообщение по ошибке, то сообщите мне по email или в чате.
    """

    def __init__(self):
        self.sender = EmailSender(email_settings)
        self._email_message = None
        self.__parsed_emails = None

    # Test emails:
    # go@yandex.ru;print; urea@gmai l.com, so@ydex.ru;print; urea@gmail.com
    def __filter_emails(self, emails: str) -> tuple[str]:
        self.__parsed_emails: tuple[str] = tuple(filter(self.re_email.findall, emails.split(";")))
        return self.__parsed_emails

    def _checking_email(self, raw_emails: str) -> tuple[str]:
        logger.debug(f"Doing with {raw_emails}")
        if self.__parsed_emails:
            return self.__parsed_emails
        emails = self.__filter_emails(raw_emails)
        if not emails:
            raise ValueError(
                "Пожалуйста, укажите хотя бы один email.\n Используйте ';' как разделитель для email'ов"
            )
        return emails

    def _send_email(self, emails: tuple[str]):
        logger.info(f"Sending emails to {emails}")
        if self._email_message is None:
            raise ValueError("Не удалось создать email. Вызовите метод create_message() раньше")
        g_emails = (Email(email, self._email_message) for email in emails)
        self.sender.execute(g_emails)
        return emails

    @property
    def type(self) -> str:
        return "email"

    def check_input(self, recipients: str) -> tuple[str]:
        return self._checking_email(recipients)

    def create_message(self, text: str):
        self._text_audio = text
        self._email_message = self.email_message_template % text

    def send(self, emails: tuple[str]):
        # Post processing
        # I don't know whether uploading file to aws
        emails = self._checking_email(emails)
        self._send_email(emails)
