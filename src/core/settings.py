from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime
from zoneinfo import ZoneInfo


class Settings(BaseSettings):


    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    def get_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DB_NAME}"


    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    def get_current_time(self) -> datetime:
        return datetime.now(tz=ZoneInfo("Asia/Tashkent"))


settings = Settings()

