from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.supabase_client import async_supabase
from app.core.exceptions import UnauthorizedError


bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:

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
    }