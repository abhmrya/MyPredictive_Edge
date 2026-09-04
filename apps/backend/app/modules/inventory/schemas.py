from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryUpsert(BaseModel):
    location_id: UUID
    sku: str = Field(..., min_length=1, max_length=150)
    stock_level: int = Field(..., ge=0)
    safety_stock_level: int = Field(default=0, ge=0)


class InventoryUpdate(BaseModel):
    stock_level: int | None = Field(default=None, ge=0)
    safety_stock_level: int | None = Field(default=None, ge=0)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    location_id: UUID
    sku: str
    stock_level: int
    safety_stock_level: int
    created_at: datetime
    updated_at: datetime
