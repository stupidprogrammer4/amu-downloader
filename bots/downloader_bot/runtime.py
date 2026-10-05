import httpx
from aiohttp import web

from downloader_bot.config.settings import BotSettings
from downloader_bot.infra.backend import BackendClient
from downloader_bot.media.runtime import MediaRuntime


class DownloaderRuntime:
    def __init__(self, settings: BotSettings):
        self.client = httpx.AsyncClient(trust_env=False)
        self.media = MediaRuntime(
            settings, BackendClient(self.client, settings)
        )

    async def startup(self, app: web.Application):
        await self.media.bot.get_me()
        await self.media.dispatcher.emit_startup()

    async def cleanup(self, app: web.Application):
        await self.media.dispatcher.emit_shutdown()
        await self.media.storage.close()
        await self.media.bot.session.close()
        await self.client.aclose()

    async def health(self, request: web.Request):
        return web.json_response({"status": "alive", "transport": "webhook"})


def create_app(settings: BotSettings | None = None) -> web.Application:
    runtime = DownloaderRuntime(settings or BotSettings.from_env())
    app = web.Application(client_max_size=1_000_000)
    runtime.media.attach(app)
    app.router.add_get("/health/live", runtime.health)
    app.on_startup.append(runtime.startup)
    app.on_cleanup.append(runtime.cleanup)
    return app


if __name__ == "__main__":
    settings = BotSettings.from_env()
    web.run_app(create_app(settings), host="0.0.0.0", port=settings.port)
