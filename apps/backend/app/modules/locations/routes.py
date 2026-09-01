from fastapi import APIRouter

from app.modules.locations.schemas import (
    LocationCreate,
    LocationResponse,
)
from app.modules.locations.services import create_location


router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


@router.post("/", response_model=LocationResponse)
async def create_location_route(location: LocationCreate):
    return await create_location(location)