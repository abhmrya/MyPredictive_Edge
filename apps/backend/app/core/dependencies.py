from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.modules.rbac.service import get_user_role_data
from app.services.supabase_client import async_supabase


bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict[str, Any]:
    """
    Validate the Supabase access token and return
    the authenticated user's basic information.
    """

    token = credentials.credentials

    try:
        response = await async_supabase.auth.get_user(token)
    except Exception:
        raise UnauthorizedError("Invalid token.")

    if not response or not response.user:
        raise UnauthorizedError("Invalid token.")

    return {
        "user_id": str(response.user.id),
        "email": response.user.email,
        "role": response.user.role,
        "name_": "Abhay Maurya",
    }


def require_permission(permission: str):
    """
    Create a FastAPI dependency that requires a specific
    permission inside an organization.
    """

    async def permission_dependency(
        organization_id: str,
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:

        user_id = current_user.get("user_id")

        if not user_id:
            raise ForbiddenError(
                "Authenticated user ID is missing."
            )

        try:
            rbac_data = await get_user_role_data(
                user_id=user_id,
                organization_id=organization_id,
            )

        except RuntimeError as exc:
            raise ForbiddenError(str(exc))

        permissions = set(
            rbac_data.get("permissions", [])
        )

        if permission not in permissions:
            raise ForbiddenError(
                "You do not have permission to perform this action."
            )

        return rbac_data

    return permission_dependency