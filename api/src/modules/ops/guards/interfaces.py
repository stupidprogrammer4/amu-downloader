from collections.abc import Awaitable
from typing import Protocol

from src.modules.ops.guards.domain.models import DownloadGuardModel


class IDownloadGuard(Protocol):
    def lock(self, key: str) -> Awaitable[DownloadGuardModel]: ...
