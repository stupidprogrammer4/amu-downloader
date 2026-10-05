from typing import Any

from papilio.errors.exceptions import ValidationException

from downloader_contracts.configuration import SettingKey, SettingScope
from downloader_contracts.media import MediaPolicy


class SettingValueValidator:
    def validate(
        self, key: SettingKey, scope: SettingScope, value: str
    ) -> str:
        try:
            parsed = MediaPolicy.model_validate_json(value)
        except ValueError as exc:
            raise ValidationException(
                message="Invalid download policy",
                message_code="invalid_setting_value",
                loc=["value"],
            ) from exc
        normalized = parsed.model_dump_json()
        if len(normalized.encode()) > 60000:
            raise ValidationException(
                message="Setting value is too large",
                message_code="setting_too_large",
                loc=["value"],
            )
        return normalized

    def schema(self, key: SettingKey) -> dict[str, Any]:
        return MediaPolicy.model_json_schema()
