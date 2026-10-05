from src.modules.ops.guards.domain.models import DownloadGuardModel
from src.modules.ops.guards.infra.mysql import DownloadGuardRepository


class DownloadGuardService:
    def __init__(self, repo: DownloadGuardRepository):
        self.repo = repo

    async def lock(self, key: str) -> DownloadGuardModel:
        result = await self.repo.lock(key)
        return result
