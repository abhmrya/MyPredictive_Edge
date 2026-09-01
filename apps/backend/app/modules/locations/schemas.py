from pydantic import BaseModel, Field
from typing import Optional


class LocationCreate(BaseModel):
    name: str
    capacity: int = Field(
        ...,
        ge=0,
        description="Capacity must be a non-negative integer"
    )
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None


class LocationResponse(BaseModel):
    message: str
    location: LocationCreate