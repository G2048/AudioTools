import logging
from collections.abc import Sequence

# from email.message import EmailMessage
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.utils import formataddr

logger = logging.getLogger("stdout")


class Email:
    def __init__(self, email: str, message: str):
        self.email = email
        self.message = message

    def __str__(self):
        return f"Email: {self.email}\nMessage: {self.message}"

    def __repr__(self):
        return self.__str__()


class EmailSender:
    def __init__(self):
        pass

    def execute(self, emails: Sequence[str]):
        pass
