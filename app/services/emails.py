import logging
import smtplib
import ssl
from collections.abc import Sequence

from app.configs.settings import EmailSettings

# from email.message import EmailMessage
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.utils import formataddr

logger = logging.getLogger("stdout")
# settings = get_email_settings()
# logger.debug(f"Email sender settings: {settings}")


class Email:
    __slots__ = ("email", "message")

    def __init__(self, email: str, message: str):
        self.email = email
        self.message = message

    def __str__(self):
        return f"Email: {self.email}\nMessage: {self.message}"

    def __repr__(self):
        return self.__str__()


class EmailSender:
    def __init__(self, settings: EmailSettings):
        self.port = settings.port
        self.host = settings.host
        self.password = settings.password
        self.sender = settings.sender

    def connect(self):
        server = smtplib.SMTP(self.host, self.port)
        _context = ssl.create_default_context()
        server.starttls(context=_context)
        server.login(self.sender, self.password)
        return server

    def quit(self):
        pass

    def __repr__(self):
        return self.__str__()

    def send(self, email: Email):
        server = self.connect()
        try:
            server.sendmail(self.sender, email.email, email.message)
        finally:
            server.quit()

    def send_batch(self, emails: Sequence[Email]):
        """
        Sends emails in a batch
        :param emails: list of emails
        :return:
        """
        pass

    def execute(self, emails: Sequence[Email]):
        """For the Action interface compliance"""
        self.send_batch(emails)
