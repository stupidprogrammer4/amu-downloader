from pydantic import BaseModel

from downloader_contracts.configuration import (
    SettingDefinitionCreate,
    SettingScope,
)


class SeedValue(BaseModel):
    key: str
    scope: SettingScope
    value: str


class ConfigurationSeed(BaseModel):
    definitions: list[SettingDefinitionCreate]
    values: list[SeedValue]
