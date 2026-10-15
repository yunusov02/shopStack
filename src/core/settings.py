from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from datetime import UTC, datetime
from sqlalchemy import URL



BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):


    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DEBUG: bool = True

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    def get_database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME
        )


    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8")

    def get_current_time(self) -> datetime:
        return datetime.now(UTC)


settings = Settings()

