
# We can now import settings directly
import os
import sys
import uuid
import time
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from contextlib import asynccontextmanager
from config_settings import get_settings

settings = get_settings()

# Test the settings to see how Pydantic validation works
print(f"Application Name: {settings.APP_NAME}")
print(f"Application Version: {settings.APP_VERSION}")
print(f"Environment: {settings.APP_ENV}")
print(f"Is Production: {settings.is_production}")
print(
    f"Scoring Parameters (VR weights): W_FLUENCY={settings.W_FLUENCY}, W_DOMAIN={settings.W_DOMAIN}, W_ADAPTIVE={settings.W_ADAPTIVE}")
print(
    f"Sum of VR weights: {settings.W_FLUENCY + settings.W_DOMAIN + settings.W_ADAPTIVE}")

# Example of how a SecretStr handles sensitive data
if settings.OPENAI_API_KEY:
    print(f"OpenAI API Key (masked): {settings.OPENAI_API_KEY}")
    # To access the actual value: settings.OPENAI_API_KEY.get_secret_value()
else:
    print("OpenAI API Key is not configured.")

# Demonstrate an invalid configuration (this will raise an error if uncommented)
# try:
#     # Temporarily modify settings to demonstrate validation failure
#     # In a real scenario, this would happen via a bad .env file or env var
#     os.environ['W_FLUENCY'] = '0.6'
#     os.environ['W_DOMAIN'] = '0.5' # This makes the sum 1.1, invalid
#     os.environ['W_ADAPTIVE'] = '0.0'
#     Settings() # This would attempt to re-parse and validate
# except ValueError as e:
#     print(f"Validation Error Caught (as expected): {e}")
# finally:
#     # Clean up env vars to not affect subsequent runs
#     for var in ['W_FLUENCY', 'W_DOMAIN', 'W_ADAPTIVE']:
#         if var in os.environ:
#             del os.environ[var]


# Placeholder for observability setup (as defined in a previous cell)
def setup_tracing(app: FastAPI):
    """Placeholder for initializing observability/tracing for the application."""
    print("Initializing observability tracing (simulated)...")


# Redefine simple APIRouter instances here to simulate router inclusion in `app`
v1_router = APIRouter()
v2_router = APIRouter()
health_router = APIRouter()  # This will be defined in the next section


@v1_router.get("/items")
async def read_v1_items():
    return {"message": "Hello from API v1"}


@v2_router.get("/items")
async def read_v2_items():
    return {"message": "Hello from API v2 - enhanced!"}

# Now, define create_app and lifespan directly within the notebook to use these local routers


@asynccontextmanager
async def lifespan_notebook(app: FastAPI):
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.APP_ENV}")
    print(f"🔢 Parameter Version: {settings.parameter_version}")
    print(
        f"🛡️ Guardrails: {'Enabled' if settings.GUARDRAILS_ENABLED else 'Disabled'}")
    print(f"💰 Cost Budget: ${settings.DAILY_COST_BUDGET_USD}/day")
    if not settings.DEBUG:
        setup_tracing(app)
    yield
    print("👋 Shutting down...")


def create_app_notebook() -> FastAPI:
    app_instance = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Individual AI-Readiness Score Platform - Production Ready",
        lifespan=lifespan_notebook,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Timing Middleware
    @app_instance.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response

    # EXCEPTION HANDLERS
    @app_instance.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Custom handler for ValueError, often from Pydantic validation failures."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "type": "validation_error",
                "request_id": getattr(request.state, 'request_id', None),
            },
        )

    @app_instance.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Custom handler for HTTPException to include request ID."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": getattr(request.state, 'request_id', None),
            },
            headers=exc.headers,
        )

    # ROUTES
    app_instance.include_router(health_router, tags=["Health"])
    app_instance.include_router(
        v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])
    app_instance.include_router(
        v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app_instance
