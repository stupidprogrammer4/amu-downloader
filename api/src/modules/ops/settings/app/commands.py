from papilio.infra.db.transaction import transaction

from downloader_contracts.configuration import SettingKey
from src.modules.ops.guards.interfaces import IDownloadGuard
from src.modules.ops.settings.app.validation import SettingValueValidator
from src.modules.ops.settings.domain.dtos import ConfigurationSeed
from src.modules.ops.settings.domain.models import (
    SettingDefinitionModel,
    SettingValueModel,
)
from src.modules.ops.settings.interfaces import (
    ISettingDefinitionService,
    ISettingValueService,
)


class ConfigurationCommands:
    def __init__(
        self,
        definitions: ISettingDefinitionService,
        values: ISettingValueService,
        guard: IDownloadGuard,
    ):
        self.definitions = definitions
        self.values = values
        self.guard = guard

    async def seed(self, data: ConfigurationSeed) -> None:
        validator = SettingValueValidator()
        prepared = [
            (
                item,
                validator.validate(
                    SettingKey(item.key), item.scope, item.value
                ),
            )
            for item in data.values
        ]
        async with transaction():
            await self.guard.lock("configuration")
            await self.definitions.seed_many(
                [
                    SettingDefinitionModel(**item.model_dump())
                    for item in data.definitions
                ]
            )
            definitions = await self.definitions.all()
            identifiers = {item.key: item.id for item in definitions}
            await self.values.seed_many(
                [
                    SettingValueModel(
                        definition_id=identifiers[SettingKey(item.key)],
                        scope=item.scope,
                        value=value,
                    )
                    for item, value in prepared
                ]
            )
