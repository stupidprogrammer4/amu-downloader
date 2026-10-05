from collections.abc import Sequence

from papilio.infra.db.tools.conflicts import handle_conflicts
from papilio.infra.db.tools.decorators import transactional

from downloader_contracts.configuration import (
    SettingDefinitionCreate,
    SettingDefinitionOut,
    SettingKey,
    SettingScope,
    SettingValueOut,
    SettingValueWrite,
)
from src.modules.ops.settings.app.validation import SettingValueValidator
from src.modules.ops.settings.domain.models import (
    SettingDefinitionModel,
    SettingValueModel,
)
from src.modules.ops.settings.infra.mysql import (
    SettingDefinitionRepository,
    SettingValueRepository,
)
from src.modules.ops.settings.interfaces import ISettingDefinitionService
from src.shared.errors import conflict, missing


class SettingDefinitionService:
    def __init__(self, repo: SettingDefinitionRepository):
        self.repo = repo

    async def get(self, key: SettingKey) -> SettingDefinitionModel:
        row = await self.repo.by_key(key)
        if row is None:
            raise missing("setting_definition", key)
        return row

    async def all(self) -> list[SettingDefinitionOut]:
        rows = await self.repo.all()
        return [
            SettingDefinitionOut.model_validate(row, from_attributes=True)
            for row in rows
        ]

    @transactional
    async def create(
        self, data: SettingDefinitionCreate
    ) -> SettingDefinitionOut:
        if await self.repo.by_key(data.key) is not None:
            raise conflict("این تعریف تنظیمات وجود دارد.")
        row = await self.repo.create(
            SettingDefinitionModel(**data.model_dump())
        )
        return SettingDefinitionOut.model_validate(row, from_attributes=True)

    async def seed_many(self, rows: Sequence[SettingDefinitionModel]) -> None:
        await self.repo.seed_many(rows)


class SettingValueService:
    def __init__(
        self,
        repo: SettingValueRepository,
        definitions: ISettingDefinitionService,
    ):
        self.repo = repo
        self.definitions = definitions
        self.validator = SettingValueValidator()

    async def get(
        self, key: SettingKey, scope: SettingScope
    ) -> SettingValueOut:
        definition = await self.definitions.get(key)
        row = await self.repo.get(definition.id, scope)
        return SettingValueOut(
            definition_id=definition.id,
            key=key,
            scope=scope,
            value_id=row.id if row else None,
            value=row.value if row else None,
            revision=row.revision if row else 0,
        )

    @handle_conflicts()
    @transactional
    async def write(
        self, key: SettingKey, scope: SettingScope, data: SettingValueWrite
    ) -> SettingValueOut:
        normalized = self.validator.validate(key, scope, data.value)
        definition = await self.definitions.get(key)
        current = await self.repo.get(definition.id, scope, lock=True)
        revision = current.revision if current else 0
        if revision != data.revision:
            raise conflict("تنظیمات تغییر کرده؛ نسخه جدید را بخوان.")
        if current is None:
            current = await self.repo.create(
                SettingValueModel(
                    definition_id=definition.id, scope=scope, value=normalized
                )
            )
        else:
            current.value = normalized
            current.revision += 1
            await self.repo.save(current)
        return SettingValueOut(
            definition_id=definition.id,
            key=key,
            scope=scope,
            value_id=current.id,
            value=current.value,
            revision=current.revision,
        )

    async def seed_many(self, rows: Sequence[SettingValueModel]) -> None:
        await self.repo.seed_many(rows)
