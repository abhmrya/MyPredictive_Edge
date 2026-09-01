from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.services.supabase_client import AsyncSupabase

from app.modules.health.routes import router as health_router
from app.modules.locations.routes import router as locations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize async Supabase client
    await AsyncSupabase.init()

    print("Supabase async client initialized")

    yield

    print("Application shutdown complete")


app = FastAPI(
    title="PredictiveEdge API",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(health_router)
app.include_router(locations_router)


@app.get("/")
async def root():
    return {
        "message": "PredictiveEdge API is running"
    }


@app.get("/supabase-check")
async def supabase_check():
    return {
        "supabase_url": settings.supabase_url,
        "client_initialized": AsyncSupabase.client is not None,
    }
