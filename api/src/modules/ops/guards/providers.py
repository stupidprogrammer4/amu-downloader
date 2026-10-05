from dishka import Provider, Scope, provide

from src.modules.ops.guards.app.services import DownloadGuardService
from src.modules.ops.guards.infra.mysql import DownloadGuardRepository
from src.modules.ops.guards.interfaces import IDownloadGuard


class GuardProvider(Provider):
    scope = Scope.REQUEST
    repository = provide(DownloadGuardRepository)
    guard = provide(DownloadGuardService, provides=IDownloadGuard)
