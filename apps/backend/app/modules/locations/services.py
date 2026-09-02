from typing import Any
from uuid import UUID

from fastapi import HTTPException

from app.modules.locations.schemas import LocationCreate, LocationUpdate
from app.services.supabase_client import async_supabase


async def create_location(location: LocationCreate) -> dict[str, Any]:
    payload = {
        "name": location.name,
        "type": location.type,
        "address": location.address,
        "city": location.city,
        "state": location.state,
        "country": location.country,
        "zip_code": location.zip_code,
        "lat": location.lat,
        "lng": location.lng,
        "capacity": location.capacity,
    }

    try:
        result = (
            await async_supabase
            .table("locations")
            .insert(payload)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create location",
            )

        print("Location created successfully:", result.data[0])  # Debugging statement
        # breakpoint()

        return result.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create location: {str(e)}",
        )
    
async def get_locations() -> list[dict[str,Any]]:
    try:
        result = (
            await async_supabase
            .table("locations")
            .select("*")
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="No locations found",
            )

        print("Locations retrieved successfully:", result.data)  # Debugging statement
        return result.data

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve locations: {str(e)}",
        )

async def get_location(location_id: UUID) -> dict[str, Any]:
    try:
        result = (
            await async_supabase.table("locations").select("*").eq("id", location_id).execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Location not found",
            )
        return result.data[0]
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve location: {str(e)}",
        )       


async def update_location(location_id: UUID,
                          location:LocationUpdate,) -> dict[str, Any]:
    payload = location.model_dump(exclude_unset=True)

    if not payload:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    try:
        result = (
            await async_supabase
            .table("locations")
            .update(payload)
            .eq("id", location_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Location not found",
            )
        print("Location updated successfully:", result.data[0])  # Debugging statement
        return result.data[0]
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update location: {str(e)}",
        )

async def delete_location(location_id: UUID) -> dict[str, Any]:
    try:
        result = (
            await async_supabase
            .table("locations")
            .delete()
            .eq("id", location_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Location not found",
            )
        return {"message": "Location deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete location: {str(e)}",
        )