import os
from typing import Any, Self

from papilio.core.config import Settings
from papilio_tasks.apps.taskiq import RedisSettings
from pydantic import BaseModel, Field, SecretStr, model_validator


class SecuritySettings(BaseModel):
    service_key: SecretStr = Field(min_length=32)
    admin_ids: list[int] = Field(min_length=1)


class TransportSettings(BaseModel):
    dry_run: bool = True
    gateway_url: str = "http://bots:8080"


class MediaRuntimeSettings(BaseModel):
    directory: str = "data/media"
    cookie_files: dict[str, str] = Field(default_factory=dict)
    metadata_threads: int = Field(default=2, ge=1, le=4)
    youtube_proxy_url: SecretStr = SecretStr("")
    youtube_token_provider_url: str = ""
    spotify_client_id: SecretStr = SecretStr("")
    spotify_client_secret: SecretStr = SecretStr("")
    spotify_access_token: SecretStr = SecretStr("")


class DownloaderAppSettings(Settings):
    security: SecuritySettings
    transport: TransportSettings = Field(default_factory=TransportSettings)
    tasks: RedisSettings
    media: MediaRuntimeSettings = Field(default_factory=MediaRuntimeSettings)

    @model_validator(mode="before")
    @classmethod
    def environment(cls, raw: Any) -> Any:
        data = dict(raw)
        security = dict(data.get("security", {}))
        if key := os.getenv("DOWNLOADER_SERVICE_KEY"):
            security["service_key"] = key
        if ids := os.getenv("DOWNLOADER_ADMIN_USER_IDS"):
            security["admin_ids"] = [int(x.strip()) for x in ids.split(",")]
        data["security"] = security
        database = dict(data.get("db", {}))
        if dsn := os.getenv("DOWNLOADER_DATABASE_URL"):
            database["dsn"] = dsn
        data["db"] = database
        tasks = dict(data.get("tasks", {}))
        if url := os.getenv("DOWNLOADER_REDIS_URL"):
            tasks["url"] = url
        data["tasks"] = tasks
        transport = dict(data.get("transport", {}))
        if dry := os.getenv("DOWNLOADER_DRY_RUN"):
            if dry.lower() not in {"true", "false"}:
                raise ValueError("DOWNLOADER_DRY_RUN must be true or false")
            transport["dry_run"] = dry.lower() == "true"
        data["transport"] = transport
        media = dict(data.get("media", {}))
        for environment, field in (
            ("DOWNLOADER_YOUTUBE_PROXY_URL", "youtube_proxy_url"),
            (
                "DOWNLOADER_YOUTUBE_TOKEN_PROVIDER_URL",
                "youtube_token_provider_url",
            ),
            ("DOWNLOADER_SPOTIFY_CLIENT_ID", "spotify_client_id"),
            ("DOWNLOADER_SPOTIFY_CLIENT_SECRET", "spotify_client_secret"),
            ("DOWNLOADER_SPOTIFY_ACCESS_TOKEN", "spotify_access_token"),
        ):
            if value := os.getenv(environment):
                media[field] = value
        data["media"] = media
        return data

    @model_validator(mode="after")
    def validate_runtime(self) -> Self:
        if self.db is None or not self.db.dsn.startswith("mysql+aiomysql://"):
            raise ValueError("Configure MySQL with the aiomysql driver")
        return self
