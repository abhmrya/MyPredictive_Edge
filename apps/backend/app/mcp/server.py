from uuid import UUID

from mcp.server.fastmcp import FastMCP

from app.modules.inventory.adapter import inventory_adapter
from app.services.supabase_client import AsyncSupabase


mcp = FastMCP("predictive-edge-inventory")


async def _initialize_dependencies() -> None:
    """Initialize dependencies for the standalone stdio MCP process."""
    await AsyncSupabase.init()


@mcp.tool()
async def get_inventory(organization_id: str, location_id: str | None = None) -> list[dict]:
    """Read inventory for an organization, optionally limited to one location."""
    await _initialize_dependencies()
    return await inventory_adapter.list(
        UUID(organization_id),
        UUID(location_id) if location_id else None,
    )


@mcp.tool()
async def get_inventory_item(organization_id: str, inventory_id: str) -> dict:
    """Read one organization-scoped inventory item by ID."""
    await _initialize_dependencies()
    return await inventory_adapter.get(UUID(organization_id), UUID(inventory_id))


if __name__ == "__main__":
    mcp.run(transport="stdio")
