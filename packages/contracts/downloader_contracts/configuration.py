from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SettingKey(StrEnum):
    MEDIA = "media.policy"


class SettingScope(StrEnum):
    GLOBAL = "global"


class SettingDefinitionCreate(BaseModel):
    key: SettingKey
    title: str = Field(min_length=1, max_length=100)


class SettingDefinitionOut(SettingDefinitionCreate):
    id: int
    kind: Literal["json"]


class SettingValueWrite(BaseModel):
    value: str = Field(min_length=2, max_length=50000)
    revision: int = Field(ge=0)


class SettingValueOut(BaseModel):
    definition_id: int
    key: SettingKey
    scope: SettingScope
    value_id: int | None
    value: str | None
    revision: int


class SettingSchemaOut(BaseModel):
    schema_definition: dict
