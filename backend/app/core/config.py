from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VELTRIX MINER API"
    environment: str = "development"
    app_version: str = "0.1.0"
    database_url: str | None = None
    coingecko_base_url: str = "https://api.coingecko.com"
    coingecko_api_key: str | None = None
    web_origin: str | None = None

    @field_validator("web_origin")
    @classmethod
    def validate_web_origin(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        origin = value.strip()
        parsed = urlsplit(origin)
        local_host = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if (
            parsed.scheme not in {"https", "http"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
            or (parsed.scheme != "https" and not (parsed.scheme == "http" and local_host))
        ):
            raise ValueError("WEB_ORIGIN must be one exact HTTPS origin (HTTP is allowed only for localhost).")
        return origin.rstrip("/")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
