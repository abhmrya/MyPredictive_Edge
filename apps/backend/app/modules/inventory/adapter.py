from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.inventory.schemas import InventoryUpdate, InventoryUpsert
from app.services.supabase_client import async_supabase


class InventoryAdapter(Protocol):
    async def list(self, organization_id: UUID, location_id: UUID | None = None) -> list[dict[str, Any]]: ...
    async def get(self, organization_id: UUID, inventory_id: UUID) -> dict[str, Any]: ...
    async def upsert(self, organization_id: UUID, payload: InventoryUpsert) -> dict[str, Any]: ...
    async def update(self, organization_id: UUID, inventory_id: UUID, payload: InventoryUpdate) -> dict[str, Any]: ...


class SupabaseInventoryAdapter:
    """Persistence adapter used by REST and MCP interfaces."""

    async def list(self, organization_id: UUID, location_id: UUID | None = None) -> list[dict[str, Any]]:
        query = (
            async_supabase.table("inventory")
            .select("*")
            .eq("organization_id", str(organization_id))
            .order("sku")
        )
        if location_id is not None:
            query = query.eq("location_id", str(location_id))
        result = await query.execute()
        return result.data or []

    async def get(self, organization_id: UUID, inventory_id: UUID) -> dict[str, Any]:
        result = (
            await async_supabase.table("inventory")
            .select("*")
            .eq("organization_id", str(organization_id))
            .eq("id", str(inventory_id))
            .limit(1)
            .execute()
        )
        if not result.data:
            raise NotFoundError("Inventory item not found.")
        return result.data[0]

    async def upsert(self, organization_id: UUID, payload: InventoryUpsert) -> dict[str, Any]:
        location = (
            await async_supabase.table("locations")
            .select("id")
            .eq("organization_id", str(organization_id))
            .eq("id", str(payload.location_id))
            .limit(1)
            .execute()
        )
        if not location.data:
            raise NotFoundError("Location not found in this organization.")

        item = payload.model_dump()
        item["organization_id"] = str(organization_id)
        item["location_id"] = str(payload.location_id)
        item["sku"] = payload.sku.strip()
        if not item["sku"]:
            raise BadRequestError("SKU cannot be blank.")

        result = (
            await async_supabase.table("inventory")
            .upsert(item, on_conflict="organization_id,location_id,sku")
            .execute()
        )
        if not result.data:
            raise BadRequestError("Failed to save inventory item.")
        return result.data[0]

    async def update(self, organization_id: UUID, inventory_id: UUID, payload: InventoryUpdate) -> dict[str, Any]:
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise BadRequestError("No fields provided for update.")
        changes["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.get(organization_id, inventory_id)
        result = (
            await async_supabase.table("inventory")
            .update(changes)
            .eq("organization_id", str(organization_id))
            .eq("id", str(inventory_id))
            .execute()
        )
        if not result.data:
            raise BadRequestError("Failed to update inventory item.")
        return result.data[0]


inventory_adapter: InventoryAdapter = SupabaseInventoryAdapter()
