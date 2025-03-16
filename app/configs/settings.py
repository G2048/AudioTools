from typing import Optional

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .log_settings import set_appname, set_appversion, set_debug_level
from .pyproject import ParserPyproject

load_dotenv()
pyproject_parser = ParserPyproject()


class AppSettings(BaseSettings):
    appname: str = ParserPyproject.name
    appversion: str = ParserPyproject.version
    debug: bool = False

    @computed_field(return_type=str)
    def appname_log(self) -> str:
        return self.appname.lower().replace(" ", "_")


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


class AwsSettingsConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AWS_")

    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str


class AwsBucketSettingsConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AWS_")

    bucket_name: str
    object_path: str
    directory_path: str


class NeuralSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLMMODEL_")

    name: str


_app_settings = AppSettings()


set_debug_level(_app_settings.debug)
set_appname(_app_settings.appname_log)
set_appversion(_app_settings.appversion)


def get_app_settings() -> AppSettings:
    return _app_settings


def get_database_settings() -> DataBaseSettings:
    return DataBaseSettings()


def get_email_settings() -> EmailSettings:
    return EmailSettings()


def get_aws_settings() -> AwsSettingsConfig:
    return AwsSettingsConfig()


def get_aws_bucket_settings() -> AwsBucketSettingsConfig:
    return AwsBucketSettingsConfig()


def get_neural_settings() -> NeuralSettings:
    return NeuralSettings()
