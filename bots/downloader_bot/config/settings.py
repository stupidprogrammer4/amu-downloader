import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr


class BotSettings(BaseModel):
    media_token: SecretStr | None = None
    media_webhook_secret: SecretStr | None = Field(default=None, min_length=32)
    media_directory: str = "data/media"
    service_key: SecretStr = Field(min_length=32)
    admin_ids: set[int] = Field(min_length=1)
    api_url: str = "http://api:8000"
    redis_url: str = "redis://redis:6379/0"
    webhook_base_url: str = ""
    port: int = Field(default=8080, ge=1, le=65535)

    @classmethod
    def from_env(cls):
        load_dotenv(os.getenv("DOWNLOADER_ENV_FILE", ".env"))
        return cls(
            media_token=SecretStr(token)
            if (token := os.getenv("DOWNLOADER_BOT_TOKEN"))
            else None,
            media_webhook_secret=SecretStr(secret)
            if (secret := os.getenv("DOWNLOADER_WEBHOOK_SECRET"))
            else None,
            media_directory=os.getenv(
                "DOWNLOADER_MEDIA_DIRECTORY", "data/media"
            ),
            service_key=SecretStr(os.getenv("DOWNLOADER_SERVICE_KEY", "")),
            admin_ids={
                int(value.strip())
                for value in os.getenv("DOWNLOADER_ADMIN_USER_IDS", "").split(
                    ","
                )
                if value.strip()
            },
            api_url=os.getenv("DOWNLOADER_API_URL", "http://api:8000"),
            redis_url=os.getenv(
                "DOWNLOADER_REDIS_URL", "redis://redis:6379/0"
            ),
            webhook_base_url=os.getenv("DOWNLOADER_WEBHOOK_BASE_URL", ""),
            port=int(os.getenv("DOWNLOADER_BOTS_PORT", "8080")),
        )
