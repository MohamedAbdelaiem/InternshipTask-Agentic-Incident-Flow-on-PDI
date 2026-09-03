# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    # ServiceNow PDI Instance Configuration
    sn_instance_url: str = "https://devXXXXXX.service-now.com"
    sn_username: str = "admin"
    sn_password: str = ""

    # Google Gemini Configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
