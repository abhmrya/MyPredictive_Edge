from typing import Any
from uuid import UUID

from app.core.exceptions import (
    AppError,
    BadRequestError,
    NotFoundError,
)
from app.modules.locations.schemas import (
    LocationCreate,
    LocationUpdate,
)
from app.services.supabase_client import async_supabase


async def create_location(
    organization_id: str,
    payload: LocationCreate,
) -> dict[str, Any]:

    try:
        organization_uuid = UUID(organization_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid organization ID."
        )

    try:
        # Verify organization exists
        organization_result = (
            await async_supabase
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

        if not organization["is_active"]:
            raise BadRequestError(
                "Organization is inactive."
            )

        location_payload = {
            "organization_id": str(organization_uuid),
            "name": payload.name.strip(),
            "type": payload.type.strip()
            if payload.type
            else None,
            "address": payload.address.strip()
            if payload.address
            else None,
            "city": payload.city.strip()
            if payload.city
            else None,
            "state": payload.state.strip()
            if payload.state
            else None,
            "country": payload.country.strip()
            if payload.country
            else None,
            "zip_code": payload.zip_code.strip()
            if payload.zip_code
            else None,
            "lat": payload.lat,
            "lng": payload.lng,
            "capacity": payload.capacity,
        }

        result = (
            await async_supabase
            .table("locations")
            .insert(location_payload)
            .execute()
        )

        if not result.data:
            raise AppError(
                "Failed to create location."
            )

        return result.data[0]

    except (BadRequestError, NotFoundError, AppError):
        raise

    except Exception as exc:
        print(
            "LOCATION CREATE ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise AppError(
            "Failed to create location."
        )


async def get_locations(
    organization_id: str,
) -> list[dict[str, Any]]:

    try:
        UUID(organization_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid organization ID."
        )

    try:
        result = (
            await async_supabase
            .table("locations")
            .select("*")
            .eq("organization_id", organization_id)
            .order("created_at", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as exc:
        print(
            "LOCATION LIST ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise AppError(
            "Failed to fetch locations."
        )


async def get_location(
    organization_id: str,
    location_id: str,
) -> dict[str, Any]:

    try:
        UUID(organization_id)
        UUID(location_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid organization ID or location ID."
        )

    try:
        result = (
            await async_supabase
            .table("locations")
            .select("*")
            .eq("id", location_id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            raise NotFoundError(
                "Location not found."
            )

        return result.data[0]

    except NotFoundError:
        raise

    except Exception as exc:
        print(
            "LOCATION GET ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise AppError(
            "Failed to fetch location."
        )


async def update_location(
    organization_id: str,
    location_id: str,
    payload: LocationUpdate,
) -> dict[str, Any]:

    try:
        UUID(organization_id)
        UUID(location_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid organization ID or location ID."
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise BadRequestError(
            "No fields provided for update."
        )

    for field in [
        "name",
        "type",
        "address",
        "city",
        "state",
        "country",
        "zip_code",
    ]:
        if field in update_data and update_data[field] is not None:
            update_data[field] = update_data[field].strip()

    try:
        existing = (
            await async_supabase
            .table("locations")
            .select("id")
            .eq("id", location_id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )

        if not existing.data:
            raise NotFoundError(
                "Location not found."
            )

        result = (
            await async_supabase
            .table("locations")
            .update(update_data)
            .eq("id", location_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise AppError(
                "Failed to update location."
            )

        return result.data[0]

    except (NotFoundError, BadRequestError, AppError):
        raise

    except Exception as exc:
        print(
            "LOCATION UPDATE ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise AppError(
            "Failed to update location."
        )


async def delete_location(
    organization_id: str,
    location_id: str,
) -> None:

    try:
        UUID(organization_id)
        UUID(location_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid organization ID or location ID."
        )

    try:
        existing = (
            await async_supabase
            .table("locations")
            .select("id")
            .eq("id", location_id)
            .eq("organization_id", organization_id)
            .limit(1)
            .execute()
        )

        if not existing.data:
            raise NotFoundError(
                "Location not found."
            )

        await (
            async_supabase
            .table("locations")
            .delete()
            .eq("id", location_id)
            .eq("organization_id", organization_id)
            .execute()
        )

    except (NotFoundError, BadRequestError):
        raise

    except Exception as exc:
        print(
            "LOCATION DELETE ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise AppError(
            "Failed to delete location."
        )