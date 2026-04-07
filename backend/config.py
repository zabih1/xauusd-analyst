from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    NEWS_API_KEY: Optional[str] = None
    MT5_LOGIN: Optional[int] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None
    ANALYSIS_INTERVAL_SECONDS: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
