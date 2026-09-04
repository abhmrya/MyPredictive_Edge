import asyncio

from app.modules.rbac.permissions import Permissions
from app.services.supabase_client import AsyncSupabase, async_supabase


ADMIN_PERMISSIONS = [
    Permissions.ORGANIZATION_VIEW,
    Permissions.ORGANIZATION_MANAGE,

    Permissions.INVENTORY_VIEW,
    Permissions.INVENTORY_MANAGE,

    Permissions.ALERTS_VIEW,
    Permissions.ALERTS_MANAGE,

    Permissions.DECISIONS_VIEW,
    Permissions.DECISIONS_APPROVE,
    Permissions.DECISIONS_REJECT,
    Permissions.DECISIONS_OVERRIDE,
]


async def seed_permissions():
    await AsyncSupabase.init()

    # Get all active ADMIN roles
    roles_result = await (
        async_supabase
        .table("organization_roles")
        .select("id, organization_id, name")
        .eq("name", "ADMIN")
        .eq("is_active", True)
        .execute()
    )

    roles = roles_result.data or []

    if not roles:
        print("No active ADMIN roles found.")
        return

    for role in roles:
        role_id = role["id"]

        print(
            f"Seeding permissions for "
            f"organization={role['organization_id']}"
        )

        for permission in ADMIN_PERMISSIONS:

            existing_result = await (
                async_supabase
                .table("organization_role_permissions")
                .select("id")
                .eq("role_id", role_id)
                .eq("permission", permission)
                .limit(1)
                .execute()
            )

            if existing_result.data:
                print(f"  EXISTS: {permission}")
                continue

            await (
                async_supabase
                .table("organization_role_permissions")
                .insert(
                    {
                        "role_id": role_id,
                        "permission": permission,
                    }
                )
                .execute()
            )

            print(f"  ADDED:  {permission}")

    print("RBAC permission seeding completed.")


if __name__ == "__main__":
    asyncio.run(seed_permissions())
    