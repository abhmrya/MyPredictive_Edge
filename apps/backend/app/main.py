from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from app.core.exceptions import AppError
from app.core.config import settings

from app.services.supabase_client import AsyncSupabase

from app.utils.logger import log_event
from app.utils.log_context import (
    clear_log_context,
    set_log_context,
)


from app.modules.health.routes import router as health_router
from app.modules.locations.routes import router as locations_router
from app.modules.auth.routes import router as auth_router
from app.modules.organizations.router import router as organization_router
from app.modules.rbac.router import router as rbac_router
from app.modules.locations.routes import router as locations_router


from app.core.exceptions import NotFoundError
from fastapi.exceptions import RequestValidationError

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize async Supabase client
    await AsyncSupabase.init()

    print("Supabase async client initialized")

    yield

    print("Application shutdown complete")

async def myfunc(request: Request):
    # breakpoint()
    print(request.url.hostname)
    print(request.body)
    print(request.method)
    print(request.url.scheme)
    # print(request.headers['content-type'])
    print(dir(request))
    print(dir(request))
    print(repr(request))
    print("DEPENDENCY RUNNING:", request.method, request.url.path)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,

    dependencies=[Depends(myfunc)],
    # root_path="/api/v1/abhay",

)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    log_event(
        "ERROR",
        "Application error: %s",
        exc.message,
        event_name="app_error",
        status_code=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        location = error.get("loc", [])

        field = location[-1] if location else "input"

        errors.append(
            {
                "field": str(field),
                "message": error.get(
                    "msg",
                    "Invalid value",
                ),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    log_event(
        "ERROR",
        "Unhandled server error",
        event_name="unhandled_exception",
        status_code=500,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
        },
    )

# ==========================================
# Security Headers Middleware
# ==========================================

@app.middleware("http")
async def security_headers_middleware(
    request: Request,
    call_next,
):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "x-request-id"
    ) or str(uuid4())

    correlation_id = request.headers.get(
        "x-correlation-id"
    ) or request_id

    client_ip = (
        request.client.host
        if request.client
        else "-"
    )

    set_log_context(
        request_id=request_id,
        correlation_id=correlation_id,
        http_method=request.method,
        http_path=request.url.path,
        client_ip=client_ip,
    )

    request.state.request_id = request_id
    request.state.correlation_id = correlation_id

    start = perf_counter()

    try:
        response = await call_next(request)

    except Exception:

        duration_ms = round(
            (perf_counter() - start) * 1000,
            2,
        )

        log_event(
            "ERROR",
            "HTTP %s %s failed",
            request.method,
            request.url.path,
            event_name="http_request",
            status_code=500,
            duration_ms=duration_ms,
            exc_info=True,
        )

        clear_log_context()

        raise

    duration_ms = round(
        (perf_counter() - start) * 1000,
        2,
    )

    log_event(
        "INFO",
        "HTTP %s %s completed",
        request.method,
        request.url.path,
        event_name="http_request",
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Correlation-ID"] = correlation_id

    clear_log_context()

    return response



# ==========================================
# CORS Middleware
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "PUT",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-Correlation-ID",
    ],
)


# ==========================================
# Routers
# ==========================================

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(locations_router)
app.include_router(organization_router)
app.include_router(rbac_router)
app.include_router(locations_router)



# ==========================================
# Root
# ==========================================

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# ==========================================
# Supabase Check
# ==========================================

@app.get("/supabase-check")
async def supabase_check():
    return {
        "supabase_url": settings.supabase_url,
        "client_initialized": AsyncSupabase.client is not None,
    }

#  ***********   testing **********

# @app.get("/test-error")
# async def test_error():
#     raise NotFoundError("This is a test error")


# @app.get("/test-500")
# async def test_500():
#     result = 10 / 0
#     return {"result": result}


from fastapi import Depends
from app.core.dependencies import get_current_user

@app.get("/api/test-auth")
async def test_auth(
    current_user: dict = Depends(get_current_user),
):
    return {
        "message": "Authentication successful",
        "user": current_user,
    }


@app.middleware("http")
async def my_middleware(request: Request, call_next):
    print("MYFUNC:", request.method, request.url.path)

    response = await call_next(request)

    return response
