from collections.abc import Sequence

from papilio.infra.db.repositories.backends.mysql import MySQLRepository
from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert
from sqlmodel import col

from downloader_contracts.configuration import SettingKey, SettingScope
from src.modules.ops.settings.domain.models import (
    SettingDefinitionModel,
    SettingValueModel,
)
from src.modules.ops.settings.infra.tables import (
    SettingDefinitionTable,
    SettingValueTable,
)


class SettingDefinitionRepository(MySQLRepository[SettingDefinitionModel]):
    table = SettingDefinitionTable

    async def by_key(self, key: SettingKey) -> SettingDefinitionModel | None:
        result = await self.uow.execute(
            select(self.table).where(col(self.table.key) == key)
        )
        return result.scalar_one_or_none()

    async def all(self) -> Sequence[SettingDefinitionModel]:
        result = await self.uow.execute(
            select(self.table).order_by(col(self.table.id))
        )
        return result.scalars().all()

    async def seed_many(self, rows: Sequence[SettingDefinitionModel]) -> None:
        if not rows:
            return
        stmt = insert(self.table).values([row.to_row() for row in rows])
        await self.uow.execute(
            stmt.on_duplicate_key_update(key=stmt.inserted.key)
        )


class SettingValueRepository(MySQLRepository[SettingValueModel]):
    table = SettingValueTable

    async def get(
        self, definition_id: int, scope: SettingScope, lock: bool = False
    ) -> SettingValueModel | None:
        stmt = select(self.table).where(
            col(self.table.definition_id) == definition_id,
            col(self.table.scope) == scope,
        )
        if lock:
            stmt = stmt.with_for_update().execution_options(
                populate_existing=True
            )
        result = await self.uow.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, row: SettingValueModel) -> None:
        await self.uow.execute(
            update(self.table)
            .execution_options(synchronize_session=False)
            .where(col(self.table.id) == row.id)
            .values(value=row.value, revision=row.revision)
        )

    async def seed_many(self, rows: Sequence[SettingValueModel]) -> None:
        if not rows:
            return
        stmt = insert(self.table).values([row.to_row() for row in rows])
        await self.uow.execute(
            stmt.on_duplicate_key_update(
                definition_id=stmt.inserted.definition_id
            )
        )
