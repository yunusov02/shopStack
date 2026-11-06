from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 5672

    DEBUG: bool = False
    ENV: Environment = Environment.DEVELOPMENT

    @property
    def database_url(self) -> str:
        return f"postgres://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return (
            f"amqp://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/"
        )


# print(Settings().model_dump())
