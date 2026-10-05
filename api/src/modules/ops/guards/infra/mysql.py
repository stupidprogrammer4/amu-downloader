from papilio.infra.db.repositories.backends.mysql import MySQLRepository
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlmodel import col

from src.modules.ops.guards.domain.models import DownloadGuardModel
from src.modules.ops.guards.infra.tables import DownloadGuardTable


class DownloadGuardRepository(MySQLRepository[DownloadGuardModel]):
    table = DownloadGuardTable

    async def lock(self, key: str) -> DownloadGuardModel:
        stmt = insert(self.table).values(key=key)
        await self.uow.execute(
            stmt.on_duplicate_key_update(key=stmt.inserted.key)
        )
        result = await self.uow.execute(
            select(self.table)
            .where(col(self.table.key) == key)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one()
