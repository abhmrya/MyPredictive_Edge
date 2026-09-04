import asyncio
from collections import defaultdict
from typing import Any
from uuid import UUID

from cachetools import TTLCache

from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)

from app.modules.rbac.permissions import VALID_PERMISSIONS
from app.modules.rbac.schemas import (
    CreateRoleRequest,
)

from app.services.supabase_client import async_supabase
from app.utils.logger import log_event


# Cache RBAC data for 5 minutes.
# Key: (user_id, organization_id)
rbac_cache: TTLCache = TTLCache(
    maxsize=1000,
    ttl=300,
)


# Prevent multiple concurrent requests for the same
# user/organization from hitting the database simultaneously.
_rbac_locks: defaultdict[
    tuple[str, str],
    asyncio.Lock,
] = defaultdict(asyncio.Lock)


async def get_user_role_data(
    user_id: str,
    organization_id: str,
) -> dict[str, Any]:
    """
    Fetch the user's role and permissions for an organization.

    Lookup flow:

        organization_members
                ↓
        organization_roles
                ↓
        organization_role_permissions

    Results are cached for 5 minutes.
    """

    cache_key = (user_id, organization_id)

    # 1. Check cache
    if cache_key in rbac_cache:
        return rbac_cache[cache_key]

    # 2. Prevent duplicate concurrent database queries
    async with _rbac_locks[cache_key]:

        # Check cache again after acquiring the lock.
        if cache_key in rbac_cache:
            return rbac_cache[cache_key]

        try:
            # 3. Find user's organization membership
            member_result = await (
                async_supabase
                .table("organization_members")
                .select("role_id, organization_id")
                .eq("user_id", user_id)
                .eq("organization_id", organization_id)
                .limit(1)
                .execute()
            )

            print("========== RBAC DEBUG ==========")
            print("USER ID:", user_id)
            print("ORG ID:", organization_id)
            print("MEMBER DATA:", member_result.data)
            print("MEMBER COUNT:", len(member_result.data or []))
            print("================================")

            if not member_result.data:
                log_event(
                    "WARNING",
                    "User is not a member of the organization",
                    event_name="rbac_membership_missing",
                    extra={
                        "user_id": user_id,
                        "organization_id": organization_id,
                    },
                )

                raise RuntimeError(
                    "Organization membership not found."
                )

            membership = member_result.data[0]
            role_id = membership.get("role_id")

            if not role_id:
                log_event(
                    "WARNING",
                    "Organization member has no role assigned",
                    event_name="rbac_role_missing",
                    extra={
                        "user_id": user_id,
                        "organization_id": organization_id,
                    },
                )

                raise RuntimeError(
                    "Organization role not found."
                )

            # 4. Fetch organization role
            role_result = await (
                async_supabase
                .table("organization_roles")
                .select("id, name, is_active")
                .eq("id", role_id)
                .eq("organization_id", organization_id)
                .limit(1)
                .execute()
            )

            if not role_result.data:
                log_event(
                    "WARNING",
                    "Organization role not found",
                    event_name="rbac_role_not_found",
                    extra={
                        "user_id": user_id,
                        "organization_id": organization_id,
                        "role_id": role_id,
                    },
                )

                raise RuntimeError(
                    "Organization role not found."
                )

            role = role_result.data[0]

            # 5. Make sure role is active
            if not role.get("is_active", False):
                log_event(
                    "WARNING",
                    "Organization role is inactive",
                    event_name="rbac_role_inactive",
                    extra={
                        "user_id": user_id,
                        "organization_id": organization_id,
                        "role_id": role_id,
                    },
                )

                raise RuntimeError(
                    "Organization role is inactive."
                )

            # 6. Fetch role permissions
            permission_result = await (
                async_supabase
                .table("organization_role_permissions")
                .select("permission")
                .eq("role_id", role_id)
                .execute()
            )

            permissions = [
                item["permission"]
                for item in (permission_result.data or [])
                if item.get("permission")
            ]

            # 7. Build RBAC data
            role_data = {
                "user_id": user_id,
                "organization_id": organization_id,
                "role_id": role_id,
                "role_name": role["name"],
                "permissions": permissions,
            }

            # 8. Store in cache
            rbac_cache[cache_key] = role_data

            log_event(
                "INFO",
                "RBAC data loaded successfully",
                event_name="rbac_data_loaded",
                extra={
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "role_id": role_id,
                },
            )

            return role_data

        except Exception as exc:
            log_event(
                "ERROR",
                "Failed to fetch RBAC data",
                event_name="rbac_fetch_failed",
                extra={
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "error": str(exc),
                },
            )

            raise


async def create_organization_role(
    payload: CreateRoleRequest,
    organization_id: str,
) -> dict[str, Any]:
    """
    Create a new custom role inside an organization.

    Newly created roles have no permissions by default.
    Permissions are assigned separately.
    """

    # 1. Validate organization UUID
    try:
        organization_uuid = UUID(organization_id)
    except (ValueError, TypeError):
        raise BadRequestError("Invalid organization ID.")

    # 2. Clean role name
    role_name = payload.name.strip()

    if not role_name:
        raise BadRequestError(
            "Role name cannot be empty."
        )

    try:
        # 3. Verify organization exists and is active
        organization_result = await (
            async_supabase
            .table("organizations")
            .select("id, is_active")
            .eq("id", str(organization_uuid))
            .limit(1)
            .execute()
        )

        if not organization_result.data:
            raise NotFoundError(
                "Organization not found."
            )

        organization = organization_result.data[0]

        if not organization.get("is_active", False):
            raise BadRequestError(
                "Organization is inactive."
            )

        # 4. Check duplicate role name
        existing_role_result = await (
            async_supabase
            .table("organization_roles")
            .select("id")
            .eq(
                "organization_id",
                str(organization_uuid),
            )
            .eq("name", role_name)
            .limit(1)
            .execute()
        )

        if existing_role_result.data:
            raise ConflictError(
                "A role with this name already exists "
                "in this organization."
            )

        # 5. Create role
        role_result = await (
            async_supabase
            .table("organization_roles")
            .insert(
                {
                    "organization_id": str(organization_uuid),
                    "name": role_name,
                    "description": payload.description,
                    "is_active": True,
                }
            )
            .execute()
        )

        if not role_result.data:
            raise RuntimeError(
                "Failed to create organization role."
            )

        role = role_result.data[0]

        # 6. Log successful creation
        log_event(
            "INFO",
            "Organization role created successfully",
            event_name="rbac_role_created",
            extra={
                "organization_id": str(organization_uuid),
                "role_id": role["id"],
                "role_name": role["name"],
            },
        )

        return role

    except (
        BadRequestError,
        ConflictError,
        NotFoundError,
    ):
        raise

    except Exception as exc:
        log_event(
            "ERROR",
            "Failed to create organization role",
            event_name="rbac_role_creation_failed",
            extra={
                "organization_id": str(organization_uuid),
                "error": str(exc),
            },
        )

        raise RuntimeError(
            "Failed to create organization role."
        )