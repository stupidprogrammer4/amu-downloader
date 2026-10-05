from collections.abc import Sequence
from typing import Protocol

from downloader_contracts.configuration import (
    SettingDefinitionCreate,
    SettingDefinitionOut,
    SettingKey,
    SettingScope,
    SettingValueOut,
    SettingValueWrite,
)
from src.modules.ops.settings.domain.dtos import ConfigurationSeed
from src.modules.ops.settings.domain.models import (
    SettingDefinitionModel,
    SettingValueModel,
)


class ISettingDefinitionService(Protocol):
    async def get(self, key: SettingKey) -> SettingDefinitionModel: ...

    async def all(self) -> list[SettingDefinitionOut]: ...

    async def create(
        self, data: SettingDefinitionCreate
    ) -> SettingDefinitionOut: ...

    async def seed_many(
        self, rows: Sequence[SettingDefinitionModel]
    ) -> None: ...


class ISettingValueService(Protocol):
    async def get(
        self, key: SettingKey, scope: SettingScope
    ) -> SettingValueOut: ...

    async def write(
        self, key: SettingKey, scope: SettingScope, data: SettingValueWrite
    ) -> SettingValueOut: ...

    async def seed_many(self, rows: Sequence[SettingValueModel]) -> None: ...


class IConfigurationCommands(Protocol):
    async def seed(self, data: ConfigurationSeed) -> None: ...
