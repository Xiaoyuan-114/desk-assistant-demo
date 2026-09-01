from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", Path(__file__).resolve().parents[1] / ".env"),
        extra="ignore",
    )
    agent_llm_base_url: str = "https://api.deepseek.com"
    agent_llm_api_key: str = ""
    agent_llm_model: str = "deepseek-chat"
    agent_llm_timeout_seconds: float = 45
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def data_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path
