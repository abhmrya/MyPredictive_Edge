import asyncio

from supabase import create_client, Client
from supabase._async.client import (
    create_client as create_async_client,
    AsyncClient,
)

from app.core.config import settings


class SyncSupabase:
    client: Client | None = None

    @classmethod
    def init(cls):
        if cls.client is None:
            if (
                not settings.supabase_url
                or not settings.supabase_service_role_key
            ):
                raise RuntimeError("Missing Supabase configuration.")

            cls.client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key,
            )

        return cls.client


class SyncClientProxy:
    def __getattr__(self, name):
        if SyncSupabase.client is None:
            SyncSupabase.init()

        return getattr(SyncSupabase.client, name)


supabase = SyncClientProxy()


class AsyncSupabase:
    client: AsyncClient | None = None
    _init_lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def init(cls):
        async with cls._init_lock:
            if cls.client is None:
                cls.client = await create_async_client(
                    settings.supabase_url,
                    settings.supabase_service_role_key,
                )

        return cls.client


async def get_async_client() -> AsyncClient:
    return await AsyncSupabase.init()


class AsyncClientProxy:
    def __getattr__(self, name):
        if AsyncSupabase.client is None:
            raise RuntimeError(
                "AsyncSupabase not initialized. "
                "Call AsyncSupabase.init() in lifespan."
            )

        return getattr(AsyncSupabase.client, name)


async_supabase = AsyncClientProxy()