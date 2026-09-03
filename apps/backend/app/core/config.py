import os

from dotenv import load_dotenv


# Load environment variables
load_dotenv(".env.local")
load_dotenv(".env", override=False)


def env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class Settings:

    # =========================
    # Application
    # =========================

    app_name: str = os.environ.get(
        "APP_NAME",
        "PredictiveEdge API",
    )

    app_version: str = os.environ.get(
        "APP_VERSION",
        "1.0.0",
    )

    is_production: bool = env_bool(
        "IS_PRODUCTION",
        False,
    )

    # =========================
    # Backend
    # =========================

    backend_url: str = os.environ.get(
        "BACKEND_URL",
        "http://localhost:8001",
    )

    frontend_origin: str = os.environ.get(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

    # =========================
    # Supabase
    # =========================

    supabase_url: str = os.environ.get(
        "SUPABASE_URL",
        "",
    )

    supabase_service_role_key: str = os.environ.get(
        "SUPABASE_SECRET_KEY",
        "",
    )

    # =========================
    # Database
    # =========================

    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "",
    )

    # =========================
    # Logging
    # =========================

    log_level: str = os.environ.get(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    service_name: str = os.environ.get(
        "SERVICE_NAME",
        "predictive_edge_backend",
    )

    # =========================
    # CORS
    # =========================

    @property
    def cors_origins(self) -> list[str]:

        origins = []

        if not self.is_production:
            origins.extend(
                [
                    "http://localhost:5173",
                    "http://localhost:5000",
                    "http://localhost:5001",
                    "http://127.0.0.1:5173",
                    "http://127.0.0.1:5000",
                    "http://127.0.0.1:5001",
                ]
            )

        if (
            self.frontend_origin
            and self.frontend_origin not in origins
        ):
            origins.append(self.frontend_origin)

        return origins


settings = Settings()