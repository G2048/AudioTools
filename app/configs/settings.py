from typing import Optional

from dotenv import load_dotenv
from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .log_settings import set_appname, set_appversion, set_debug_level

load_dotenv()


class AppSettings(BaseSettings):
    appname: str = "WebUI"
    appversion: str = "0.0.1"
    debug: bool = False

    @field_validator("appname")
    def appname_is_lower(cls, value: str) -> str:
        return value.lower()


class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_")

    host: str
    port: str
    user: str
    dbname: str
    password: str
    engine: Optional[str] = "psycopg"

    @computed_field(return_type=str)
    def pg_dsn(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    host: str
    port: int = 587  # 587 for STARTTLS, 465 for SSL
    password: str
    sender: str


_app_settings = AppSettings()


set_debug_level(_app_settings.debug)
set_appname(_app_settings.appname)
set_appversion(_app_settings.appversion)


def get_appsettings() -> AppSettings:
    return _app_settings


def get_database_settings() -> DataBaseSettings:
    return DataBaseSettings()


def get_email_settings() -> EmailSettings:
    return EmailSettings()
