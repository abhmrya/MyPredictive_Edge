from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    type: str | None = Field(
        default=None,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    zip_code: str | None = Field(
        default=None,
        max_length=20,
    )

    lat: float | None = None

    lng: float | None = None

    capacity: int = Field(
        ...,
        ge=0,
        description="Capacity must be a non-negative integer",
    )


class LocationResponse(BaseModel):
    id: UUID
    name: str
    type: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zip_code: str | None = None
    lat: float | None = None
    lng: float | None = None
    capacity: int
    created_at: datetime
    updated_at: datetime


class LocationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    type: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    zip_code: str | None = Field(None, max_length=20)
    lat: float | None = None
    lng: float | None = None
    capacity: int | None = Field(None, ge=0)