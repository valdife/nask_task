from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
