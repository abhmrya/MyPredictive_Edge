from typing import Any

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.organizations.schemas import (
    OrganizationCreate,
    OrganizationResponse,
)
from app.modules.organizations.service import create_organization


router = APIRouter(
    prefix="/api/organizations",
    tags=["Organizations"],
)


@router.post("/",response_model=OrganizationResponse,)
async def create_organization_route(
    organization: OrganizationCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    return await create_organization(
        organization=organization,
        current_user=current_user,
    )