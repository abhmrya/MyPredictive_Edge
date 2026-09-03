from fastapi import APIRouter,Depends
from app.core.dependencies import get_current_user

from app.modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)

from app.modules.auth.service import (
    register_user,
    login_user,
    logout_user,
    refresh_access_token,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
)
async def register(data: RegisterRequest):
    result = await register_user(data)

    return {
        "message": (
            "Registration successful. "
            "Please check your email and verify your account before logging in."
        ),
        **result,
    }


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(data: LoginRequest):
    result = await login_user(data)

    return {
        "message": "Login successful",
        **result,
    }


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
):
    return current_user

@router.post("/logout")
async def logout():
    await logout_user()

    return {
        "message": "Logout successful"
    }

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
)
async def refresh_token(payload: RefreshTokenRequest):
    result = await refresh_access_token(payload.refresh_token)

    return result