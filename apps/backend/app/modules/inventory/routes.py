from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import require_permission
from app.modules.inventory.adapter import inventory_adapter
from app.modules.inventory.schemas import InventoryResponse, InventoryUpdate, InventoryUpsert
from app.modules.rbac.permissions import Permissions


router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


@router.get("/organizations/{organization_id}", response_model=list[InventoryResponse])
async def list_inventory(
    organization_id: UUID,
    location_id: UUID | None = Query(default=None),
    _: dict[str, Any] = Depends(require_permission(Permissions.INVENTORY_VIEW)),
):
    return await inventory_adapter.list(organization_id, location_id)


@router.get("/organizations/{organization_id}/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    organization_id: UUID,
    inventory_id: UUID,
    _: dict[str, Any] = Depends(require_permission(Permissions.INVENTORY_VIEW)),
):
    return await inventory_adapter.get(organization_id, inventory_id)


@router.put("/organizations/{organization_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
async def upsert_inventory(
    organization_id: UUID,
    payload: InventoryUpsert,
    _: dict[str, Any] = Depends(require_permission(Permissions.INVENTORY_MANAGE)),
):
    return await inventory_adapter.upsert(organization_id, payload)


@router.patch("/organizations/{organization_id}/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    organization_id: UUID,
    inventory_id: UUID,
    payload: InventoryUpdate,
    _: dict[str, Any] = Depends(require_permission(Permissions.INVENTORY_MANAGE)),
):
    return await inventory_adapter.update(organization_id, inventory_id, payload)
