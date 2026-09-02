from fastapi import APIRouter
from uuid import UUID
from app.modules.locations.schemas import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from app.modules.locations.services import (
    create_location,
    get_locations,
    get_location,
    update_location,
    delete_location
)

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


@router.post("/", response_model=LocationResponse)
async def create_location_route(location: LocationCreate):
    print("Received request to create location:", location)
    print("Location data:", location.dict())
    print("Location name:", location.name)  
    print("Location type:", location.type)
    print("location",LocationCreate)
    return await create_location(location)


@router.get("/", response_model=list[LocationResponse])
async def get_locations_route():
    return await get_locations()


@router.get("/{location_id}", response_model = LocationResponse)
async def get_location_route(location_id: UUID):
    return await get_location(location_id)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location_route(location_id: UUID, location: LocationUpdate):
    return await update_location(location_id, location)


@router.delete("/{location_id}", response_model=LocationResponse)
async def delete_location_route(location_id: UUID):
    return await delete_location(location_id)