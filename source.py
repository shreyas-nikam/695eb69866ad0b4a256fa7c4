from typing import Literal, Optional, List, Dict, Any
from functools import lru_cache
from pydantic import Field, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime, timedelta
import asyncio
import time
import uuid
import os
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# Placeholder for external modules for demonstration purposes
# In a real project, these would be separate files (e.g., air/api/routes/v1.py)
# We define simple APIRouter instances here to simulate router inclusion.
v1_router = APIRouter()
v2_router = APIRouter()

# Placeholder for observability setup, as this would involve external libraries/services
def setup_tracing(app: FastAPI):
    """Placeholder for initializing observability/tracing for the application."""
    print("Initializing observability tracing (simulated)...")
    # In a real scenario, this would integrate with OpenTelemetry, LangChain, etc.

# Helper to simulate file creation for project structure
def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Created file: {path}")

# Add the project root to the sys path for local imports
# In a real Poetry project, this is handled by `poetry run` or `poetry shell`
# For a notebook, we simulate it to allow `from air.config.settings import settings`
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

# Clean up previous runs if any to ensure fresh start for directory creation
if os.path.exists("individual-air-platform"):
    !rm -rf individual-air-platform
# 1. Create the project root directory and initialize Poetry
# In a real shell, you'd run these commands. We're simulating them.
!mkdir individual-air-platform
%cd individual-air-platform

# Initialize Poetry. The name matches the project description, and Python version is specified.
# The "^3.12" indicates compatibility with Python 3.12 and above, but not 4.0.
# The actual execution of `poetry init` would be interactive; we simulate its outcome.
!poetry init --name="individual-air-platform" --python="^3.12"

# 2. Install core Week 1 dependencies
# These are the runtime dependencies for our FastAPI application.
!poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette

# 3. Install development dependencies
# These tools are essential for code quality, testing, and static analysis during development.
# `pytest` and `pytest-asyncio` for testing, `pytest-cov` for coverage,
# `black` for code formatting, `ruff` for linting, `mypy` for static type checking,
# and `hypothesis` for property-based testing.
!poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy hypothesis

# 4. Create the standard source directory structure
# This structure organizes our application logic into logical domains:
# - `src/air`: The main application package
# - `api/routes/v1`, `api/routes/v2`: Versioned API endpoints for evolution
# - `config`: Application configuration
# - `models`: Pydantic models for data (request/response, database)
# - `services`: Business logic and external service integrations
# - `schemas`: Data schemas (often for API request/response parsing)
# - `agents`, `observability`, `mcp`, `events`: Specific modules for AI-related components
# - `tests`: For unit, integration, and evaluation tests
# - `docs`: Documentation, including Architecture Decision Records (ADR)
!mkdir -p src/air/{{api/routes/v1,api/routes/v2,config,models,services,schemas}}
!mkdir -p src/air/{{agents,observability,mcp,events}}
!mkdir -p tests/{{unit,integration,evals}}
!mkdir -p docs/{{adr,requirements,failure-modes}}

# Create an __init__.py file to make 'air' a Python package
!touch src/air/__init__.py
# Content for src/air/config/settings.py
settings_file_content = """
from typing import Literal, Optional, List, Dict, Any
from functools import lru_cache
from pydantic import Field, model_validator, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime, timedelta

class Settings(BaseSettings):
    \"\"\"Application settings with comprehensive validation.\"\"\"

    model_config = SettingsConfigDict(
          env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore", # Ignore extra fields in .env not defined in Settings
    )

    # ====================================
    # APPLICATION
    # ====================================
    APP_NAME: str = "Individual AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ====================================
    # API
    # ====================================
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ====================================
    # DATABASE
    # ====================================
    DATABASE_URL: str = "postgresql+asyncpg://air:air@localhost:5432/air_platform"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ====================================
    # REDIS
    # ====================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ====================================
    # LLM PROVIDERS
    # ====================================
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None

    # Model routing by task
    MODEL_ASSESSMENT: str = "claude-sonnet-4-20250514"
    MODEL_SCORING: str = "gpt-4-turbo"
    MODEL_CHAT: str = "claude-haiku-4-5-20251001"
    MODEL_EMBEDDING: str = "text-embedding-3-small"

    # Fallback chain for LLMs
    MODEL_FALLBACK_CHAIN: List[str] = [
          "gpt-4-turbo",
        "claude-sonnet-4-20250514",
        "gpt-3.5-turbo",
    ]

    # ====================================
    # COST MANAGEMENT (NEW in v4.0)
    # ====================================
    DAILY_COST_BUDGET_USD: float = Field(default=100.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1.0)

    # ====================================
    # SCORING PARAMETERS (v1.0)
    # All scoring parameters have explicit bounds to prevent
    # configuration errors that could produce invalid scores.
    # ====================================
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.5, le=0.7)
    BETA_SYNERGY_COEF: float = Field(default=0.15, ge=0.05, le=0.20)
    W_FLUENCY: float = Field(default=0.45, ge=0.0, le=1.0)
    W_DOMAIN: float = Field(default=0.35, ge=0.0, le=1.0)
    W_ADAPTIVE: float = Field(default=0.20, ge=0.0, le=1.0)

    THETA_TECHNICAL: float = Field(default=0.30, ge=0.0, le=1.0)
    THETA_PRODUCTIVITY: float = Field(default=0.35, ge=0.0, le=1.0)
    THETA_JUDGMENT: float = Field(default=0.20, ge=0.0, le=1.0)
    THETA_VELOCITY: float = Field(default=0.15, ge=0.0, le=1.0)

    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)
    GAMMA_EXPERIENCE: float = Field(default=0.15, ge=0.10, le=0.25)

    # ====================================
    # EXTERNAL APIS
    # ====================================
    ONET_API_URL: str = "https://services.onetcenter.org/ws/"
    ONET_API_KEY: Optional[SecretStr] = None
    BLS_API_URL: str = "https://api.bls.gov/publicAPI/v2/"
    BLS_API_KEY: Optional[SecretStr] = None

    # ====================================
    # OBSERVABILITY
    # ====================================
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    LANGSMITH_API_KEY: Optional[SecretStr] = None
    LANGSMITH_PROJECT: str = "individual-air-platform"

    # ====================================
    # GUARDRAILS
    # ====================================
    GUARDRAILS_ENABLED: bool = True
    PII_DETECTION_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # ====================================
    # BATCH PROCESSING (NEW in v4.0)
    # ====================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    BATCH_MAX_CONCURRENCY: int = 10

    @model_validator(mode='after')
    def validate_weight_sums(self) -> 'Settings':
        \"\"\"Validate that component weights sum to 1.0.\"\"\"
        # V^R weights
        vr_sum = self.W_FLUENCY + self.W_DOMAIN + self.W_ADAPTIVE
        if abs(vr_sum - 1.0) > 0.001:
            raise ValueError(f"V^R weights must sum to 1.0, got {vr_sum}")

        # Fluency weights
        fluency_sum = (self.THETA_TECHNICAL + self.THETA_PRODUCTIVITY +
                       self.THETA_JUDGMENT + self.THETA_VELOCITY)
        if abs(fluency_sum - 1.0) > 0.001:
            raise ValueError(f"Fluency weights must sum to 1.0, got {fluency_sum}")
        return self

    @computed_field
    @property
    def parameter_version(self) -> str:
        \"\"\"Return current parameter version.\"\"\"
        return "v1.0"

    @computed_field
    @property
    def is_production(self) -> bool:
        \"\"\"Check if running in production.\"\"\"
        return self.APP_ENV == "production"

@lru_cache
def get_settings() -> Settings:
    \"\"\"Cached settings instance.\"\"\"
    return Settings()

# Instantiate settings for immediate use in the notebook context
settings = get_settings()
"""

create_file("src/air/config/settings.py", settings_file_content)

# We can now import settings directly
from air.config.settings import settings

# Test the settings to see how Pydantic validation works
print(f"Application Name: {settings.APP_NAME}")
print(f"Application Version: {settings.APP_VERSION}")
print(f"Environment: {settings.APP_ENV}")
print(f"Is Production: {settings.is_production}")
print(f"Scoring Parameters (VR weights): W_FLUENCY={settings.W_FLUENCY}, W_DOMAIN={settings.W_DOMAIN}, W_ADAPTIVE={settings.W_ADAPTIVE}")
print(f"Sum of VR weights: {settings.W_FLUENCY + settings.W_DOMAIN + settings.W_ADAPTIVE}")

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

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import time
import uuid
import sys
import os


# Placeholder for observability setup (as defined in a previous cell)
def setup_tracing(app: FastAPI):
    """Placeholder for initializing observability/tracing for the application."""
    print("Initializing observability tracing (simulated)...")

# Redefine simple APIRouter instances here to simulate router inclusion in `app`
v1_router = APIRouter()
v2_router = APIRouter()
health_router = APIRouter() # This will be defined in the next section

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
    print(f"🛡️ Guardrails: {'Enabled' if settings.GUARDRAILS_ENABLED else 'Disabled'}")
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
    app_instance.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])
    app_instance.include_router(v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app_instance

# Create the FastAPI app instance using the factory
app = create_app_notebook()

# You can't directly "run" uvicorn in a Jupyter notebook cell for an extended period,
# but we can simulate the app's startup phase and demonstrate router inclusion.
print("\n--- Simulating App Startup ---")
async def simulate_startup():
    async with lifespan_notebook(app):
        print(f"App initialized with routers: ")
        for route in app.routes:
            # Check for hasattr to avoid errors on non-routing objects
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {','.join(route.methods)} {route.path}")
        print("Application is running (simulated).\n")
        # In a real environment, uvicorn would now be serving requests.
        # For demonstration, we simulate fetching an endpoint.
        # We cannot truly make HTTP requests to a non-running server from within the same cell.
        # However, we can assert that the app object and its routes are correctly configured.

# This line should be `await simulate_startup()` not part of a string for `create_file`.
# And it should be executed after `app = create_app_notebook()`.
# The previous `create_file` was for `src/air/api/main.py`. This current cell defines local
# notebook versions.
#
# The `NameError: name 'route' is not defined` from the original problem was likely a symptom of
# incorrect parsing of the `main_api_content` string itself, which then caused issues
# when that string was later referenced or the content was attempted to be interpreted.
# By ensuring the `create_app_notebook` and `lifespan_notebook` are defined directly as valid
# Python in this cell, the syntax error is resolved.
await simulate_startup()
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch
import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Define a mock settings object that mimics the `settings` object
# expected from a previous cell (e.g., from `air.config.settings`).
# This allows tests to control the settings behavior (e.g., DEBUG mode).
class MockSettings:
    def __init__(self, debug=True):
        self.DEBUG = debug
        self.APP_NAME = "Test AI-R Platform"
        self.APP_VERSION = "0.0.1"
        self.APP_ENV = "development" if debug else "production"
        self.parameter_version = "v1.0"
        self.GUARDRAILS_ENABLED = True
        self.DAILY_COST_BUDGET_USD = 100.0
        self.API_V1_PREFIX = "/api/v1"
        self.API_V2_PREFIX = "/api/v2"

    @property
    def is_production(self):
        return self.APP_ENV == "production"

# Placeholder for observability setup, mocked for tests to prevent actual side effects
def setup_tracing(app: FastAPI):
    pass

# Redefine simple APIRouter instances here. These are the actual APIRouter objects
# that `create_app_notebook` will include.
v1_router = APIRouter()
v2_router = APIRouter()
health_router = APIRouter()

# Dummy endpoints for v1, v2, and health to be included by the app factory.
# These endpoints allow us to send requests and verify routing and middleware.
@health_router.get("/health")
async def get_health():
    return {"status": "ok"}

@v1_router.get("/items")
async def read_v1_items():
    return {"message": "Hello from API v1"}

@v2_router.get("/items")
async def read_v2_items():
    return {"message": "Hello from API v2 - enhanced!"}

# Additional endpoints to test exception handlers
@v1_router.get("/raise-value-error")
async def raise_value_error_endpoint():
    raise ValueError("This is a test ValueError")

@v1_router.get("/raise-http-exception/{status_code}")
async def raise_http_exception_endpoint(status_code: int):
    raise HTTPException(status_code=status_code, detail=f"HTTP Exception for status {status_code}")


# The lifespan_notebook and create_app_notebook functions from the user's provided code.
# The code is corrected to fix the syntax error related to the `allow_headers` definition
# and other potential newline/string literal issues.
@asynccontextmanager
async def lifespan_notebook(app: FastAPI):
    # Suppress print statements during tests to keep test output clean
    # For actual tests, we only care if the lifespan context manager runs without error
    # and potentially if setup_tracing is called.
    if not settings.DEBUG: # `settings` is patched at a global level for tests
        setup_tracing(app)
    yield


def create_app_notebook() -> FastAPI:
    # `settings` is assumed to be globally available (from a previous notebook cell)
    # or will be patched by pytest fixtures.
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
        allow_headers=["*"], # Corrected from ["*\"]"
    )

    @app_instance.middleware("http")
    async def add_request_context_notebook(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response

    @app_instance.exception_handler(ValueError)
    async def value_error_handler_notebook(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "type": "validation_error",
                "request_id": getattr(request.state, 'request_id', None),
            },
        )

    @app_instance.exception_handler(HTTPException)
    async def http_exception_handler_notebook(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": getattr(request.state, 'request_id', None),
            },
            headers=exc.headers,
        )

    app_instance.include_router(health_router, tags=["Health"])
    app_instance.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])
    app_instance.include_router(v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app_instance


# --- Pytest Fixtures ---

# Fixture to provide mock settings for debug mode, patching the global `settings`
@pytest.fixture
def mock_settings_debug_true():
    # Patch the global 'settings' object (assumed to be defined in __main__ for notebooks)
    # for the duration of the test.
    with patch('__main__.settings', MockSettings(debug=True)) as mock_s:
        yield mock_s

# Fixture to provide mock settings for production mode
@pytest.fixture
def mock_settings_debug_false():
    with patch('__main__.settings', MockSettings(debug=False)) as mock_s:
        yield mock_s

# Fixture to create FastAPI app in debug mode with mocked UUID and time for deterministic tests
@pytest.fixture
def app_debug(mock_settings_debug_true):
    with patch('uuid.uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-000000000001')):
        with patch('time.perf_counter', side_effect=[100, 100.1]): # Simulate duration of 0.1s
            app = create_app_notebook()
            yield app

# Fixture to create FastAPI app in production mode
@pytest.fixture
def app_prod(mock_settings_debug_false):
    with patch('uuid.uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-000000000002')):
        with patch('time.perf_counter', side_effect=[200, 200.2]): # Simulate duration of 0.2s
            app = create_app_notebook()
            yield app

# AsyncClient for making requests to the debug app
@pytest.fixture
async def client_debug(app_debug):
    async with AsyncClient(app=app_debug, base_url="http://test") as ac:
        yield ac

# AsyncClient for making requests to the production app
@pytest.fixture
async def client_prod(app_prod):
    async with AsyncClient(app=app_prod, base_url="http://test") as ac:
        yield ac

# --- Tests ---

@pytest.mark.asyncio
async def test_app_attributes_debug_mode(app_debug):
    """Verify FastAPI app attributes are set correctly in debug mode."""
    assert app_debug.title == "Test AI-R Platform"
    assert app_debug.version == "0.0.1"
    assert app_debug.description == "Individual AI-Readiness Score Platform - Production Ready"
    assert app_debug.docs_url == "/docs"
    assert app_debug.redoc_url == "/redoc"

@pytest.mark.asyncio
async def test_app_attributes_prod_mode(app_prod):
    """Verify FastAPI app attributes are set correctly in production mode."""
    assert app_prod.title == "Test AI-R Platform"
    assert app_prod.version == "0.0.1"
    assert app_prod.description == "Individual AI-Readiness Score Platform - Production Ready"
    assert app_prod.docs_url is None
    assert app_prod.redoc_url is None

@pytest.mark.asyncio
async def test_cors_middleware_debug_mode(client_debug):
    """Verify CORS middleware behavior in debug mode (allows all origins)."""
    response = await client_debug.options("/health", headers={"Origin": "http://some-unrelated-domain.com", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
    assert "Access-Control-Allow-Credentials" in response.headers
    assert response.headers.get("Access-Control-Allow-Methods") == "*"
    assert response.headers.get("Access-Control-Allow-Headers") == "*"

@pytest.mark.asyncio
async def test_cors_middleware_prod_mode(client_prod):
    """Verify CORS middleware behavior in production mode (restricts origins)."""
    # In production, allow_origins is empty, so preflight requests from any origin are rejected
    response = await client_prod.options("/health", headers={"Origin": "http://some-unrelated-domain.com", "Access-Control-Request-Method": "GET"})
    # FastAPI's CORSMiddleware with `allow_origins=[]` rejects non-matching origins with 400.
    assert response.status_code == 400
    assert "Access-Control-Allow-Origin" not in response.headers # No allow-origin header for disallowed origins

@pytest.mark.asyncio
async def test_request_id_and_timing_middleware(client_debug):
    """Verify request ID and processing time headers are added by middleware."""
    response = await client_debug.get("/api/v1/items")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == '00000000-0000-0000-0000-000000000001' # From mock
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) == pytest.approx(0.1, abs=0.001) # From mock

@pytest.mark.asyncio
async def test_router_v1_inclusion(client_debug):
    """Verify API v1 routes are correctly included and functional."""
    response = await client_debug.get("/api/v1/items")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from API v1"}

@pytest.mark.asyncio
async def test_router_v2_inclusion(client_debug):
    """Verify API v2 routes are correctly included and functional."""
    response = await client_debug.get("/api/v2/items")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from API v2 - enhanced!"}

@pytest.mark.asyncio
async def test_health_router_inclusion(client_debug):
    """Verify health check router is correctly included and functional."""
    response = await client_debug.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_value_error_handler(client_debug):
    """Verify custom ValueError exception handler works correctly."""
    response = await client_debug.get("/api/v1/raise-value-error")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_response = response.json()
    assert json_response["detail"] == "This is a test ValueError"
    assert json_response["type"] == "validation_error"
    assert "request_id" in json_response
    assert json_response["request_id"] == '00000000-0000-0000-0000-000000000001' # From mock

@pytest.mark.asyncio
async def test_http_exception_handler_custom(client_debug):
    """Verify custom HTTPException handler works correctly."""
    test_status_code = status.HTTP_404_NOT_FOUND
    response = await client_debug.get(f"/api/v1/raise-http-exception/{test_status_code}")
    assert response.status_code == test_status_code
    json_response = response.json()
    assert json_response["detail"] == f"HTTP Exception for status {test_status_code}"
    assert "request_id" in json_response
    assert json_response["request_id"] == '00000000-0000-0000-0000-000000000001' # From mock

@pytest.mark.asyncio
async def test_http_exception_handler_fastapi_default(client_debug):
    """Verify the HTTPException handler also catches default FastAPI HTTP exceptions (like 404)."""
    response = await client_debug.get("/nonexistent-path")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    json_response = response.json()
    assert json_response["detail"] == "Not Found"
    assert "request_id" in json_response
    assert json_response["request_id"] == '00000000-0000-0000-0000-000000000001' # From mock


# Code cell (function definition + function execution)
from pydantic import BaseModel

# Content for src/air/api/routes/health.py
health_router_content = """
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Literal
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import sys

# Ensure settings are importable from the project structure
if 'src' not in sys.path:
    sys.path.insert(0, 'src')
from air.config.settings import settings

router = APIRouter()

# Pydantic Models for Health Responses
class DependencyStatus(BaseModel):
    \"\"\"Status of a single dependency.\"\"\"
    name: str
    status: Literal[\"healthy\", \"degraded\", \"unhealthy\", \"not_configured\"]
    latency_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    \"\"\"Basic health check response.\"\"\"
    status: Literal[\"healthy\", \"degraded\", \"unhealthy\"]
    version: str
    environment: str
    timestamp: datetime
    parameter_version: str

class DetailedHealthResponse(HealthResponse):
    \"\"\"Detailed health with dependency checks.\"\"\"
    dependencies: Dict[str, DependencyStatus]
    uptime_seconds: float

# Track startup time for uptime calculation
_startup_time = datetime.utcnow()

# Asynchronous functions to check individual dependencies
async def check_database() -> DependencyStatus:
    \"\"\"Check database connectivity.\"\"\"
    try:
        # In production, actually ping the database
        await asyncio.sleep(0.01) # Simulate network latency
        return DependencyStatus(
              name=\"database\",
            status=\"healthy\",
            latency_ms=10.0,
        )
    except Exception as e:
        return DependencyStatus(
              name=\"database\",
            status=\"unhealthy\",
            error=str(e),
        )

async def check_redis() -> DependencyStatus:
    \"\"\"Check Redis connectivity.\"\"\"
    try:
        # In production, actually ping Redis
        await asyncio.sleep(0.005) # Simulate network latency
        return DependencyStatus(
              name=\"redis\",
            status=\"healthy\",
            latency_ms=5.0,
        )
    except Exception as e:
        return DependencyStatus(
              name=\"redis\",
            status=\"unhealthy\",
            error=str(e),
        )

async def check_llm() -> DependencyStatus:
    \"\"\"Check LLM API availability.\"\"\"
    try:
        if not settings.OPENAI_API_KEY:
            return DependencyStatus(
                  name=\"llm\",
                status=\"not_configured\",
                latency_ms=None,
                error=\"OPENAI_API_KEY not set\"
            )
        # Would ping LLM health endpoint or make a dummy request
        await asyncio.sleep(0.02) # Simulate LLM API call latency
        return DependencyStatus(
              name=\"llm\",
            status=\"healthy\",
            latency_ms=20.0,
        )
    except Exception as e:
        return DependencyStatus(
              name=\"llm\",
            status=\"degraded\", # LLM might be degraded rather than unhealthy if it's external
            error=str(e),
        )

@router.get(\"/health\", response_model=HealthResponse, summary=\"Basic Health Check\")
async def health_check() -> HealthResponse:
    \"\"\"Basic health check - fast, no dependency checks.\"\"\"
    return HealthResponse(
          status=\"healthy\",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
    )

@router.get(\"/health/detailed\", response_model=DetailedHealthResponse, summary=\"Detailed Health Check with Dependencies\")
async def detailed_health_check() -> DetailedHealthResponse:
    \"\"\"Detailed health check with dependency status.\"\"\"
    # Check all dependencies concurrently
    db_status, redis_status, llm_status = await asyncio.gather(
          check_database(),
        check_redis(),
        check_llm(),
    )

    dependencies = {{{{}}\"database\": db_status,
        \"redis\": redis_status,
        \"llm\": llm_status,
    }}}}

    # Overall status is degraded if any dependency is unhealthy or degraded
    overall_status: Literal[\"healthy\", \"degraded\", \"unhealthy\"] = \"healthy\"
    for dep in dependencies.values():
        if dep.status == \"unhealthy\":
            overall_status = \"unhealthy\"
            break
        elif dep.status == \"degraded\":
            overall_status = \"degraded\"
        elif dep.status == \"not_configured\" and overall_status == \"healthy\":
            overall_status = \"degraded\" # Consider not_configured as degraded if no other issues

    uptime = (datetime.utcnow() - _startup_time).total_seconds()

    return DetailedHealthResponse(
          status=overall_status,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
        dependencies=dependencies,
        uptime_seconds=uptime,
    )

@router.get(\"/health/ready\", summary=\"Kubernetes Readiness Probe\")
async def readiness_check():
    \"\"\"Kubernetes readiness probe: checks if the service is ready to accept traffic.\"\"\"
    # A service is \"ready\" if all critical dependencies are healthy.
    # We use the detailed health check to determine readiness.
    health = await detailed_health_check()
    if health.status == \"unhealthy\" or health.status == \"degraded\":
        return JSONResponse(
              status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={{{{}}\"status\": \"not_ready\", \"reason\": f\"Overall status: {{{{health.status}}}}\"}}}}}
        )
    return {{{{}}\"status\": \"ready\"}}}}

@router.get(\"/health/live\", summary=\"Kubernetes Liveness Probe\")
async def liveness_check():
    \"\"\"Kubernetes liveness probe: checks if the application is alive and responsive.\"\"\"
    # A simple check that doesn't involve heavy dependency polling,
    # just ensures the application process is running and responding to HTTP requests.
    return {{{{}}\"status\": \"alive\"}}}}
"""

create_file("src/air/api/routes/health.py", health_router_content)

# We need to explicitly make `health_router` from the content above available to `app_core`.
# For the notebook, we'll assign the functions to the locally defined `health_router` object.
# This simulates the router being loaded from `src/air/api/routes/health.py`.

# (Re-)Define models
class DependencyStatus(BaseModel):
    name: str
    status: Literal["healthy", "degraded", "unhealthy", "not_configured"]
    latency_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    environment: str
    timestamp: datetime
    parameter_version: str

class DetailedHealthResponse(HealthResponse):
    dependencies: Dict[str, DependencyStatus]
    uptime_seconds: float

_startup_time = datetime.utcnow() # Reset startup time for demo

async def check_database_notebook() -> DependencyStatus:
    try:
        await asyncio.sleep(0.01)
        return DependencyStatus(name="database", status="healthy", latency_ms=10.0)
    except Exception as e:
        return DependencyStatus(name="database", status="unhealthy", error=str(e))

async def check_redis_notebook() -> DependencyStatus:
    try:
        await asyncio.sleep(0.005)
        return DependencyStatus(name="redis", status="healthy", latency_ms=5.0)
    except Exception as e:
        return DependencyStatus(name="redis", status="unhealthy", error=str(e))

async def check_llm_notebook() -> DependencyStatus:
    try:
        if not settings.OPENAI_API_KEY:
            return DependencyStatus(name="llm", status="not_configured", error="OPENAI_API_KEY not set")
        await asyncio.sleep(0.02)
        return DependencyStatus(name="llm", status="healthy", latency_ms=20.0)
    except Exception as e:
        return DependencyStatus(name="llm", status="degraded", error=str(e))


# Assign functions to the health_router object (defined earlier)
@health_router.get("/health", response_model=HealthResponse)
async def health_check_func() -> HealthResponse:
    return HealthResponse(
          status="healthy",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
    )

@health_router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check_func() -> DetailedHealthResponse:
    db_status, redis_status, llm_status = await asyncio.gather(
          check_database_notebook(),
        check_redis_notebook(),
        check_llm_notebook(),
    )
    dependencies = {"database": db_status, "redis": redis_status, "llm": llm_status}
    overall_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    for dep in dependencies.values():
        if dep.status == "unhealthy":
            overall_status = "unhealthy"
            break
        elif dep.status == "degraded":
            overall_status = "degraded"
        elif dep.status == "not_configured" and overall_status == "healthy":
            overall_status = "degraded"

    uptime = (datetime.utcnow() - _startup_time).total_seconds()
    return DetailedHealthResponse(
          status=overall_status,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
        dependencies=dependencies,
        uptime_seconds=uptime,
    )

@health_router.get("/health/ready")
async def readiness_check_func():
    health = await detailed_health_check_func()
    if health.status == "unhealthy" or health.status == "degraded":
        raise HTTPException(
              status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "reason": f"Overall status: {health.status}"},
        )
    return {"status": "ready"}

@health_router.get("/health/live")
async def liveness_check_func():
    return {"status": "alive"}

# Re-create the app_core to include the newly defined health_router endpoints
app_core = create_app_notebook()

# Simulate a request to the health endpoints to verify functionality
# In a real environment, you'd use `httpx.AsyncClient` or similar to hit these.
# Here we'll directly call the async functions within the notebook.
print("--- Testing Health Check Endpoints (simulated calls) ---")

# Test /health
basic_health_response = await health_check_func()
print(f"Basic Health Check (/health): {basic_health_response.model_dump_json(indent=2)}")

# Test /health/detailed
detailed_health_response = await detailed_health_check_func()
print(f"Detailed Health Check (/health/detailed): {detailed_health_response.model_dump_json(indent=2)}")

# Test /health/ready (successful case)
try:
    readiness_status = await readiness_check_func()
    print(f"Readiness Probe (/health/ready): {readiness_status}")
except HTTPException as e:
    print(f"Readiness Probe Failed: {e.detail}")

# Test /health/live
liveness_status = await liveness_check_func()
print(f"Liveness Probe (/health/live): {liveness_status}")
from air.config.settings import Settings, get_settings
import os

# =================================================================
# Mistake 1: Not validating weight sums
# PROBLEM: Configuration allows weights that don't sum to 1.0,
# leading to incorrect AI scoring.
# =================================================================
print("--- Mistake 1: Not validating weight sums ---")
print("# WRONG Example (if validation was absent):")
# Imagine these values are read from an .env file without Pydantic validation
W_FLUENCY_WRONG = 0.50
W_DOMAIN_WRONG = 0.40
W_ADAPTIVE_WRONG = 0.20 # Sum = 1.10, which is incorrect!
print(f"  W_FLUENCY = {W_FLUENCY_WRONG}")
print(f"  W_DOMAIN = {W_DOMAIN_WRONG}")
print(f"  W_ADAPTIVE = {W_ADAPTIVE_WRONG}")
print(f"  Sum of VR weights = {W_FLUENCY_WRONG + W_DOMAIN_WRONG + W_ADAPTIVE_WRONG} (should be 1.0!)")

# Fix: Pydantic's model_validator catches this at startup.
# We already have this implemented in src/air/config/settings.py
print("# FIX: The `model_validator` in `Settings` class catches this at startup.")
print("  Attempting to load settings with incorrect weights (simulated error):")
try:
    # Temporarily override environment variables to simulate the bad config
    os.environ['W_FLUENCY'] = '0.5'
    os.environ['W_DOMAIN'] = '0.4'
    os.environ['W_ADAPTIVE'] = '0.2'
    # Try to get settings, which will trigger validation
    Settings() # This would instantiate and validate the settings
except ValueError as e:
    print(f"  Successfully caught validation error: {e}")
finally:
    # Clean up environment variables
    for var in ['W_FLUENCY', 'W_DOMAIN', 'W_ADAPTIVE']:
        if var in os.environ:
            del os.environ[var]
    # Re-initialize settings to the correct ones (from defaults or original .env)
    global settings
    settings = get_settings()
print(f"  Current (valid) settings: W_FLUENCY={settings.W_FLUENCY}, Sum={settings.W_FLUENCY + settings.W_DOMAIN + settings.W_ADAPTIVE}")


# =================================================================
# Mistake 2: Exposing secrets in logs
# PROBLEM: Sensitive API keys or credentials are logged directly,
# creating a security vulnerability.
# =================================================================
print("--- Mistake 2: Exposing secrets in logs ---")
print("# WRONG Example: Logging the actual API key directly.")
dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
print(f"  Using key: {dummy_api_key}") # This would print the full key!

# Fix: Use Pydantic's SecretStr. It masks values upon string conversion.
print("# FIX: Use `SecretStr` which masks values.")
# Set a dummy secret key via environment variable for demonstration
os.environ['OPENAI_API_KEY'] = dummy_api_key
global settings # Ensure we're using the global settings object
settings = get_settings() # Reload settings to pick up new env var

print(f"  OpenAI API Key (using SecretStr): {settings.OPENAI_API_KEY}")
print(f"  Type of key: {type(settings.OPENAI_API_KEY)}")
# To access the raw value (only when strictly necessary, e.g., passing to an API client):
# print(f"  Actual raw key (use with caution): {settings.OPENAI_API_KEY.get_secret_value()}")

# Clean up environment variable
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']
settings = get_settings() # Reload settings to remove the dummy key


# =================================================================
# Mistake 3: Missing lifespan context manager
# PROBLEM: Resources (database connections, thread pools) are not
# properly cleaned up on application shutdown, leading to leaks.
# =================================================================
print("--- Mistake 3: Missing lifespan context manager ---")
print("# WRONG Example: FastAPI app without a lifespan context manager.")
# app = FastAPI() # Resources leak on shutdown!
# print("  FastAPI app initialized without lifespan. (Resources would leak!)")

# Fix: Always use `asynccontextmanager` for FastAPI's `lifespan`.
# We have already implemented this in `create_app_notebook()` and `lifespan_notebook()`.
print("# FIX: Always use `asynccontextmanager` for `lifespan` for proper startup/shutdown.")
print("  Our `create_app_notebook()` uses `lifespan_notebook`:")

# We can re-run the startup simulation to show the effect
async def verify_lifespan_fix():
    print("  Simulating app startup with lifespan:")
    async with lifespan_notebook(app_core):
        print("    Application started up (resources initialized).")
    print("    Application shut down (resources cleaned up).")

await verify_lifespan_fix()