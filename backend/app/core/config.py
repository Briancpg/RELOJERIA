from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Watch Repair SaaS"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(default="postgresql+psycopg://watch:watch@postgres:5432/watch")
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"

    app_timezone: str = "America/Santo_Domingo"
    app_currency: str = "DOP"

    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_base_url: str = ""
    max_image_upload_mb: int = 10

    openai_api_key: str = ""
    openai_vision_model: str = "gpt-5.4-mini"
    openai_vision_timeout_seconds: int = 45

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
