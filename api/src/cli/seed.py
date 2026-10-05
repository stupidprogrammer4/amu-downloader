import asyncio
import os
from pathlib import Path

from dishka import make_async_container
from dotenv import load_dotenv
from papilio.core.config import get_settings

from src.config.providers import task_providers
from src.config.settings import DownloaderAppSettings
from src.modules.ops.settings.domain.dtos import ConfigurationSeed
from src.modules.ops.settings.interfaces import IConfigurationCommands


async def seed() -> None:
    load_dotenv(os.getenv("DOWNLOADER_ENV_FILE", ".env"))
    settings = get_settings(DownloaderAppSettings)
    container = make_async_container(*task_providers(settings))
    try:
        async with container() as scope:
            commands = await scope.get(IConfigurationCommands)
            await commands.seed(
                ConfigurationSeed.model_validate_json(
                    Path("api/seeds/defaults.json").read_text()
                )
            )
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(seed())
