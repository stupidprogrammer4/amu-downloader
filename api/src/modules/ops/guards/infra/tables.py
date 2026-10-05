from papilio.infra.db.table import BaseTable

from src.modules.ops.guards.domain.models import DownloadGuardModel


class DownloadGuardTable(DownloadGuardModel, BaseTable, table=True):
    pass
