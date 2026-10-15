import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import URL



BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):


    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DEBUG: bool = True

    def get_database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host="localhost",
            port=5432,
            database=self.DB_NAME
        )


    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8")

    def get_current_time(self) -> datetime:
        return datetime.now(tz=ZoneInfo("Asia/Tashkent"))


settings = Settings()

