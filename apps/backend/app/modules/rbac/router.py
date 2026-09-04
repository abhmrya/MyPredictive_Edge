from typing import Any

from fastapi import APIRouter, Depends

from app.core.dependencies import require_permission
from app.modules.rbac.permissions import Permissions
from app.modules.rbac.schemas import (
    CreateRoleRequest,
    RoleResponse,
)
from app.modules.rbac.service import create_organization_role


router = APIRouter(
    prefix="/api/v1/rbac",
    tags=["RBAC"],
)


@router.post(
    "/organizations/{organization_id}/roles",
    response_model=RoleResponse,
)
async def create_role(
    organization_id: str,
    payload: CreateRoleRequest,
    rbac_data: dict[str, Any] = Depends(
        require_permission(
            Permissions.ORGANIZATION_MANAGE
        )
    ),
) -> dict[str, Any]:
    """
    Create a custom role inside an organization.

    Required permission:
        organization.manage
    """

    return await create_organization_role(
        payload=payload,
        organization_id=organization_id,
    )