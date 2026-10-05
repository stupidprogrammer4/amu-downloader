import asyncio
from urllib.parse import urlsplit

from aiogram import Bot

from downloader_bot.config.settings import BotSettings


async def register() -> None:
    settings = BotSettings.from_env()
    origin = settings.webhook_base_url.rstrip("/")
    if urlsplit(origin).scheme != "https" or settings.media_token is None:
        raise ValueError("A bot token and public HTTPS origin are required")
    if settings.media_webhook_secret is None:
        raise ValueError("A webhook secret is required")
    async with Bot(settings.media_token.get_secret_value()) as bot:
        registered = await bot.set_webhook(
            origin + "/telegram/media",
            secret_token=settings.media_webhook_secret.get_secret_value(),
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,
        )
    if not registered:
        raise RuntimeError("Webhook registration failed")


if __name__ == "__main__":
    asyncio.run(register())
