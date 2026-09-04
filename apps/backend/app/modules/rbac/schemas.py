from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateRoleRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Role name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Role description",
    )


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    is_active: bool