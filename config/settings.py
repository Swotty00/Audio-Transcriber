from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    vosk_model_path: str = "models/vosk"
    data_dir: str = "data"

    sample_rate: int = 16000

    ai_api_key: str = ""

    log_level: str = "INFO"
    max_file_size_mb: int = 500

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level deve ser um de: {allowed}")
        return v.upper()

    @property
    def ai_enabled(self) -> bool:
        return bool(self.anthropic_api_key)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()