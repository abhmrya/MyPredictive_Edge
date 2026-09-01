import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SECRET_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")


settings = Settings()