from dishka import Provider, Scope, provide

from src.modules.ops.settings.app.commands import ConfigurationCommands
from src.modules.ops.settings.app.services import (
    SettingDefinitionService,
    SettingValueService,
)
from src.modules.ops.settings.infra.mysql import (
    SettingDefinitionRepository,
    SettingValueRepository,
)
from src.modules.ops.settings.interfaces import (
    IConfigurationCommands,
    ISettingDefinitionService,
    ISettingValueService,
)


class ConfigurationProvider(Provider):
    scope = Scope.REQUEST
    definitions = provide(SettingDefinitionRepository)
    values = provide(SettingValueRepository)
    definition_service = provide(
        SettingDefinitionService, provides=ISettingDefinitionService
    )
    value_service = provide(SettingValueService, provides=ISettingValueService)

    commands = provide(ConfigurationCommands, provides=IConfigurationCommands)
