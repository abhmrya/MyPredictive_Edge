from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_permission
from app.modules.locations.schemas import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from app.modules.locations.services import (
    create_location,
    delete_location,
    get_location,
    get_locations,
    update_location,
)
from app.modules.rbac.permissions import Permissions


router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Locations"],
)


@router.post(
    "/organizations/{organization_id}",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_location_route(
    organization_id: str,
    payload: LocationCreate,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.INVENTORY_MANAGE
        )
    ),
):
    return await create_location(
        organization_id=organization_id,
        payload=payload,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=list[LocationResponse],
)
async def list_locations_route(
    organization_id: str,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.INVENTORY_VIEW
        )
    ),
):
    return await get_locations(
        organization_id=organization_id,
    )


@router.get(
    "/organizations/{organization_id}/{location_id}",
    response_model=LocationResponse,
)
async def get_location_route(
    organization_id: str,
    location_id: str,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.INVENTORY_VIEW
        )
    ),
):
    return await get_location(
        organization_id=organization_id,
        location_id=location_id,
    )


@router.patch(
    "/organizations/{organization_id}/{location_id}",
    response_model=LocationResponse,
)
async def update_location_route(
    organization_id: str,
    location_id: str,
    payload: LocationUpdate,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.INVENTORY_MANAGE
        )
    ),
):
    return await update_location(
        organization_id=organization_id,
        location_id=location_id,
        payload=payload,
    )


@router.delete(
    "/organizations/{organization_id}/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_location_route(
    organization_id: str,
    location_id: str,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.INVENTORY_MANAGE
        )
    ),
):
    await delete_location(
        organization_id=organization_id,
        location_id=location_id,
    )

    return None