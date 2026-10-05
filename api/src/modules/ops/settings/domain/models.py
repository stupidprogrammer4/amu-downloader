from papilio.infra.db.schema.entity import PersistenceEntity
from papilio.infra.db.schema.fields import (
    CharField,
    ForeignKeyField,
    IntField,
    TextField,
)

from downloader_contracts.configuration import SettingKey, SettingScope


class SettingDefinitionModel(PersistenceEntity):
    key: SettingKey = CharField(100, unique=True)
    title: str = CharField(100)
    kind: str = CharField(20, default="json")


class SettingValueModel(PersistenceEntity):
    definition_id: int = ForeignKeyField(
        "tbl_setting_definitions.id", ondelete="CASCADE"
    )
    scope: SettingScope = CharField(20)
    value: str = TextField()
    revision: int = IntField(default=1)
