from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Location name",
    )

    type: str | None = Field(
        default=None,
        max_length=100,
        description="Location type such as warehouse, store, factory",
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

    lat: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude",
    )

    lng: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude",
    )

    capacity: int = Field(
        ...,
        ge=0,
        description="Maximum storage capacity",
    )


class LocationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
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

    lat: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    lng: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    capacity: int | None = Field(
        default=None,
        ge=0,
    )


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID

    name: str
    type: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    zip_code: str | None

    lat: float | None
    lng: float | None

    capacity: int

    created_at: object
    updated_at: object