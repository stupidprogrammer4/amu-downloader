from papilio.infra.db.schema.entity import BaseEntity
from papilio.infra.db.schema.fields import CharField


class DownloadGuardModel(BaseEntity):
    key: str = CharField(96, primary_key=True)
