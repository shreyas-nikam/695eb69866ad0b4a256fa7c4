import os
import time
import uuid
import asyncio
from typing import Literal, Optional, List
from functools import lru_cache
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
project_root = "individual-air-platform"
os.makedirs(project_root, exist_ok=True)
os.chdir(project_root) # Simulate changing into the project directory

# Create source and test directories
os.makedirs("src/air/api/routes/v1", exist_ok=True)
os.makedirs("src/air/api/routes/v2", exist_ok=True)
os.makedirs("src/air/config", exist_ok=True)
os.makedirs("src/air/models", exist_ok=True)
os.makedirs("src/air/services", exist_ok=True)
os.makedirs("src/air/schemas", exist_ok=True)
os.makedirs("src/air/agents", exist_ok=True)
os.makedirs("src/air/observability", exist_ok=True)
os.makedirs("src/air/mcp", exist_ok=True)
os.makedirs("src/air/events", exist_ok=True)
os.makedirs("tests/unit", exist_ok=True)
os.makedirs("tests/integration", exist_ok=True)
os.makedirs("tests/evals", exist_ok=True)

# Create an __init__.py in src/air to make it a Python package
with open("src/air/__init__.py", "w") as f:
    pass

# Create empty __init__.py files for relevant directories to ensure they are treated as packages
for path in [
    "src/air/api", "src/air/api/routes", "src/air/api/routes/v1", "src/air/api/routes/v2",
    "src/air/config", "src/air/models", "src/air/services", "src/air/schemas"
]:
    with open(f"{path}/__init__.py", "w") as f:
        pass

# Create an empty pyproject.toml as a placeholder for Poetry initialization
with open("pyproject.toml", "w") as f:
    f.write("""[tool.poetry]\nname = "individual-air-platform"\nversion = "0.1.0"\ndescription = ""\nauthors = ["Your Name <you@example.com>"]\nreadme = "README.md"\npackages = [{\"include\" = \"air\", \"from\" = \"src\"}]\n\n[tool.poetry.dependencies]\npython = "^3.12"\nfastapi = "*"\nuvicorn = {\"extras\" = [\"standard\"], \"version\" = \"*\"}\npydantic = "*"\npydantic-settings = "*"\nhttpx = "*"\nsse-starlette = "*"\n\n\n[tool.poetry.group.dev.dependencies]\npytest = "*"\npytest-asyncio = "*"\npytest-cov = "*"\nblack = "*"\nruff = "*"\nmypy = "*"\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n""")

print("Project directory structure and Poetry initialization conceptually completed.")
print("Placeholder files and directories created:")
# Walk the created structure to display it
for root, dirs, files in os.walk("."):
    level = root.replace("./", "").count(os.sep)
    indent = ' ' * 4 * (level)
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        print(f"{indent}    {f}")
class Settings(BaseSettings):
    """Application settings with comprehensive validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Application details
    APP_NAME: str = "Individual AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # API version prefixes
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"

    # Database connection URLs
    DATABASE_URL: str = "postgresql+asyncpg://air:air@localhost:5432/air_platform"
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Providers API keys
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None

    # Cost Management parameters
    DAILY_COST_BUDGET_USD: float = Field(default=100.0, ge=0, description="Daily budget for external API costs in USD")

    # Scoring Parameters for AI models
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.5, le=0.7, description="Weight for Alpha VR component")
    BETA_SYNERGY_COEF: float = Field(default=0.15, ge=0.05, le=0.20, description="Coefficient for Beta synergy factor")

    # Component weights for a hypothetical AI scoring model (e.g., for user experience)
    W_FLUENCY: float = Field(default=0.45, ge=0.0, le=1.0, description="Weight for fluency component")
    W_DOMAIN: float = Field(default=0.35, ge=0.0, le=1.0, description="Weight for domain expertise component")
    W_ADAPTIVE: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for adaptiveness component")

    GAMMA_EXPERIENCE: float = Field(default=0.15, ge=0.10, le=0.25, description="Gamma experience factor")

    @model_validator(mode='after')
    def validate_weight_sums(self) -> 'Settings':
        """
        Validate that the component weights for the V^R scoring model sum to 1.0.
        This ensures correct normalization and consistency in scoring.
        """
        vr_sum = self.W_FLUENCY + self.W_DOMAIN + self.W_ADAPTIVE
        if abs(vr_sum - 1.0) > 0.001:
            raise ValueError(f"V^R weights must sum to 1.0. Got {vr_sum:.2f} (W_FLUENCY={self.W_FLUENCY}, W_DOMAIN={self.W_DOMAIN}, W_ADAPTIVE={self.W_ADAPTIVE})")
        return self

@lru_cache
def get_settings() -> Settings:
    """Cached function to get application settings."""
    return Settings()

settings = get_settings()

print(f"Application Name: {settings.APP_NAME}")
print(f"Application Version: {settings.APP_VERSION}")
print(f"Environment: {settings.APP_ENV}")
print(f"API v1 Prefix: {settings.API_V1_PREFIX}")
print(f"LLM API Key (masked by SecretStr): {settings.OPENAI_API_KEY}")
print(f"Daily Cost Budget: ${settings.DAILY_COST_BUDGET_USD}")
print(f"VR Weights: Fluency={settings.W_FLUENCY}, Domain={settings.W_DOMAIN}, Adaptive={settings.W_ADAPTIVE}")
print(f"Sum of VR Weights: {settings.W_FLUENCY + settings.W_DOMAIN + settings.W_ADAPTIVE:.2f}")

print("\n--- Demonstrating Validation Failure (Incorrect VR Weights - Mistake 1) ---")
try:
    os.environ['W_FLUENCY'] = '0.50'
    os.environ['W_DOMAIN'] = '0.40'
    os.environ['W_ADAPTIVE'] = '0.25'

    get_settings.cache_clear()

    print("Attempting to load settings with W_FLUENCY=0.50, W_DOMAIN=0.40, W_ADAPTIVE=0.25...")
    invalid_settings = get_settings()
    print(f"Successfully loaded settings with invalid weights (unexpected): {invalid_settings.W_FLUENCY + invalid_settings.W_DOMAIN + invalid_settings.W_ADAPTIVE}")
except ValueError as e:
    print(f"Configuration validation failed as expected: {e}")
except Exception as e:
    print(f"An unexpected error occurred during validation test: {e}")
finally:
    if 'W_FLUENCY' in os.environ: del os.environ['W_FLUENCY']
    if 'W_DOMAIN' in os.environ: del os.environ['W_DOMAIN']
    if 'W_ADAPTIVE' in os.environ: del os.environ['W_ADAPTIVE']
    get_settings.cache_clear()
    settings = get_settings()

print("\n--- Demonstrating SecretStr for API Keys (Mistake 2: Exposing secrets in logs) ---")
try:
    os.environ['OPENAI_API_KEY'] = 'sk-supersecretkey12345_for_demo_only'
    get_settings.cache_clear()
    settings_with_secret = get_settings()
    print(f"OPENAI_API_KEY (should be masked): {settings_with_secret.OPENAI_API_KEY}")
    print(f"Accessing raw secret value: {settings_with_secret.OPENAI_API_KEY.get_secret_value()[:10]}...")
except Exception as e:
    print(f"Error demonstrating SecretStr: {e}")
finally:
    if 'OPENAI_API_KEY' in os.environ: del os.environ['OPENAI_API_KEY']
    get_settings.cache_clear()
    settings = get_settings()
health_router = APIRouter()
@health_router.get("/health", summary="Health Check", tags=["Health"])
async def health_check_endpoint():
    """Checks the health of the application."""
    return {"status": "ok", "version": settings.APP_VERSION, "name": settings.APP_NAME, "env": settings.APP_ENV}

v1_router = APIRouter()
@v1_router.get("/status", summary="Get V1 Status", tags=["Version 1"])
async def get_v1_status():
    """Returns the status for API v1."""
    return {"message": f"Welcome to {settings.APP_NAME} API v1", "version": settings.APP_VERSION}

v2_router = APIRouter()
@v2_router.get("/status", summary="Get V2 Status", tags=["Version 2"])
async def get_v2_status():
    """Returns the status for API v2 - Newer & Shinier!"""
    return {"message": f"Welcome to {settings.APP_NAME} API v2 - Advanced Features", "version": settings.APP_VERSION}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown events for the FastAPI application.
    This ensures resources are initialized and cleaned up properly.
    (Addresses Mistake 3: Missing lifespan context manager)
    """
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.APP_ENV} environment...")
    await asyncio.sleep(0.05)
    print("✨ Application startup complete: Database connections, cache initialized.")
    yield
    print("👋 Shutting down application...")
    await asyncio.sleep(0.05)
    print("🛑 Application shutdown complete: Resources released.")

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.
    This utilizes the Application Factory Pattern for flexible setup.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None
    )

    # --- Middleware Stack ---

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        """
        Adds a unique request ID (X-Request-ID) and measures request processing time (X-Process-Time)
        as custom headers to the response.
        """
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response

    # --- API Routes ---

    app.include_router(health_router, tags=["Health"])

    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX)

    return app

app = create_app()

print("FastAPI application setup conceptually complete.")
print(f"Application Title: {app.title}")
print(f"Application Version: {app.version}")
print(f"API v1 Prefix configured: {settings.API_V1_PREFIX}")
print(f"API v2 Prefix configured: {settings.API_V2_PREFIX}")
print("API versioning structure is established using FastAPI's APIRouter.")
print(f"API v1 endpoints will be accessible under the prefix: {settings.API_V1_PREFIX}")
print(f"API v2 endpoints will be accessible under the prefix: {settings.API_V2_PREFIX}")
print("The '/health' endpoint is available at the root level for service monitoring.")
print("This separation enables independent development and deployment of API versions.")
print("--- Conceptualizing Production Infrastructure ---")
print("\n**Containerization (Docker):**")
print("Alex plans to create a `Dockerfile` in the project root (`./`) to define the application's runtime environment.")
print("This `Dockerfile` will specify the base Python image, install Poetry, add application code, and define the command to run the FastAPI application using Uvicorn.")
print("For local development and multi-service orchestration, a `docker-compose.yml` file would be used to define how the FastAPI service, along with dependencies like PostgreSQL and Redis, run together in an isolated development environment.")
print("Example conceptual files:")
print("  - `Dockerfile` (in project root)")
print("  - `docker-compose.yml` (in project root)")

print("\n**Continuous Integration (GitHub Actions):**")
print("Alex will define a GitHub Actions workflow to automate testing and code quality checks.")
print("This workflow, typically located in `.github/workflows/ci.yml`, will execute tasks like:")
print("  - Installing Python dependencies with Poetry.")
print("  - Running `black` for consistent code formatting.")
print("  - Running `ruff` for fast code linting.")
print("  - Executing `pytest` for comprehensive unit and integration tests.")
print("  - Checking code coverage with `pytest-cov` to ensure sufficient test coverage.")
print("Example conceptual file:")
print("  - `.github/workflows/ci.yml`")

print("\nThese foundational steps, while not fully implemented here, are critical for ensuring the production-readiness, reliability, and maintainability of the AI platform.")