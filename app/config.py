from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "silode"
    display_name: str = "Silode"
    host: str = "127.0.0.1"
    port: int = 11435
    default_model: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    max_tokens: int = 256
    temperature: float = 0.7
    allow_stub_runtime: bool = True
    available_models: str = ""
    system_prompt: str = (
        "You are Silode, a polished local assistant for Mac users. "
        "Be concise, helpful, and practical."
    )
    desktop_width: int = 1320
    desktop_height: int = 860

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SILODE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
