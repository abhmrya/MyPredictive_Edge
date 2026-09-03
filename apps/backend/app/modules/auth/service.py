from app.core.exceptions import BadRequestError
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.services.supabase_client import async_supabase


async def register_user(data: RegisterRequest) -> dict:
    try:
        response = await async_supabase.auth.sign_up(
            {
                "email": data.email,
                "password": data.password,
            }
        )

        if not response.user:
            raise BadRequestError("Unable to create user.")

        return {
            "email": response.user.email,
            "email_verification_required": response.session is None,
        }

    except BadRequestError:
        raise
    except Exception:
        raise BadRequestError("Unable to register user.")

    

async def login_user(data: LoginRequest) -> dict:
    try:
        async_supabase.auth
        response = await async_supabase.auth.sign_in_with_password(
            {
                "email": data.email,
                "password": data.password,
            }
        )

        print("EMAIL CONFIRMED:", response.user.email_confirmed_at)

        if not response.user or not response.session:
            raise BadRequestError("Invalid email or password.")

        return {
            "user_id": str(response.user.id),
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except BadRequestError:
        raise

    except Exception:
        raise BadRequestError("Invalid email or password.")


async def logout_user() -> None:
    try:
        await async_supabase.auth.sign_out()
    except Exception:
        raise BadRequestError("Unable to logout user.")


async def refresh_access_token(refresh_token: str) -> dict:
    try:
        response = await async_supabase.auth.refresh_session(refresh_token)

        if not response.session:
            raise BadRequestError("Invalid refresh token.")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except BadRequestError:
        raise

    except Exception:
        raise BadRequestError("Invalid refresh token.")