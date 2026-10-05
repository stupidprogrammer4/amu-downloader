from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from papilio.api.responses.envelope import APIResponse

from downloader_contracts.configuration import (
    SettingKey,
    SettingSchemaOut,
    SettingScope,
    SettingValueOut,
    SettingValueWrite,
)
from src.config.security import owner_auth, service_auth
from src.modules.ops.settings.app.validation import SettingValueValidator
from src.modules.ops.settings.interfaces import ISettingValueService

router = APIRouter(
    prefix="/internal/configuration",
    tags=["Configuration"],
    route_class=DishkaRoute,
    dependencies=[Depends(service_auth), Depends(owner_auth)],
)


@router.get("/schema/{key}")
async def schema(key: SettingKey) -> APIResponse[SettingSchemaOut, None]:
    return APIResponse.from_data(
        SettingSchemaOut(schema_definition=SettingValueValidator().schema(key))
    )


@router.get(
    "/values/{key}/{scope}", response_model=APIResponse[SettingValueOut, None]
)
async def value(
    key: SettingKey,
    scope: SettingScope,
    service: FromDishka[ISettingValueService],
):
    result = await service.get(key, scope)
    return APIResponse.from_data(result)


@router.put(
    "/values/{key}/{scope}", response_model=APIResponse[SettingValueOut, None]
)
async def write_value(
    key: SettingKey,
    scope: SettingScope,
    data: SettingValueWrite,
    service: FromDishka[ISettingValueService],
):
    result = await service.write(key, scope, data)
    return APIResponse.from_data(result)
