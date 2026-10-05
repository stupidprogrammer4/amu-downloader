import os

from dotenv import load_dotenv
from papilio.api.application import create_app
from papilio.core.config import get_settings

from src.config.providers import infrastructure_providers
from src.config.settings import DownloaderAppSettings

load_dotenv(os.getenv("DOWNLOADER_ENV_FILE", ".env"))
settings = get_settings(DownloaderAppSettings)
app = create_app(
    settings,
    providers=infrastructure_providers(settings),
    middleware=[],
)
