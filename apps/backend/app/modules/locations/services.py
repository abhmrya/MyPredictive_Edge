from typing import Any

from fastapi import HTTPException

from app.modules.locations.schemas import LocationCreate
from app.services.supabase_client import async_supabase


async def create_location(location: LocationCreate) -> dict[str, Any]:
    payload = {
        "name": location.name,
        "capacity": location.capacity,
        "address": location.address,
        "city": location.city,
        "state": location.state,
        "country": location.country,
        "zip_code": location.zip_code,
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

        return {
            "message": "Location created successfully",
            "location": result.data[0],
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create location: {str(e)}",
        )