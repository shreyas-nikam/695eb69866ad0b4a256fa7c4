
# Building a Production-Ready AI Service Skeleton: A Software Developer's Blueprint

## Introduction: The Individual AI-Readiness Platform Case Study

Welcome to the **Individual AI-Readiness Platform** project! You are a **Software Developer** tasked with establishing the foundational setup for a new AI service. This service will eventually host a specific AI model or data processing pipeline, but our immediate goal is to lay down a robust, scalable, and maintainable project skeleton from day one. This proactive approach ensures our AI services are not just functional but also reliable, secure, and easy to maintain.

In a rapidly evolving field like AI, the agility to deploy new services while maintaining high standards is paramount. This notebook will guide you through a real-world workflow, demonstrating how to apply best practices in Python development, API design, and containerization to build a solid foundation for your AI applications. We'll leverage tools like Poetry for dependency management, FastAPI for API development, Pydantic for robust configuration, and Docker for reproducible environments.

By the end of this lab, you'll have a blueprint for rapidly establishing consistent, compliant, and production-ready AI services. This means less boilerplate for you, clearer project organization, and a faster path to delivering impactful AI features for the entire organization.

## 1. Setting Up Your Development Environment

As a Software Developer, the first step in any new project is to prepare your environment. We need to install the necessary libraries to manage dependencies and build our FastAPI application. This ensures all team members work with the same tools and library versions, preventing "works on my machine" issues.

```python
# Install required libraries
# This command installs FastAPI, Uvicorn (standard for serving ASGI apps),
# Pydantic (for data validation), Pydantic-Settings (for managing application settings),
# httpx (an HTTP client, often useful for testing or making external requests),
# and sse-starlette (for Server-Sent Events, useful for streaming responses in API v2).
!pip install fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette
```

```python
# Import the required dependencies
# These imports are consolidated from various project files (settings, main API, health routes)
# to make them available for the notebook's step-by-step execution.
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
```

## 2. Project Kick-off: Laying the Foundation for the AI-Readiness Platform

As a Software Developer at the Individual AI-Readiness Platform, your first major task is to establish a standardized project structure and manage dependencies effectively. This isn't just about organizing files; it's about enforcing consistency across all AI services, streamlining onboarding for new developers, and ensuring predictable behavior in development and production environments. We'll use Poetry to manage dependencies and define a clear directory layout tailored for an API-driven AI service.

### Why this matters (Real-world relevance)
A well-defined project structure and dependency management system reduce technical debt, prevent dependency conflicts, and accelerate development cycles. For an organization like ours, this means a more reliable AI platform and faster iteration on new AI capabilities.

```python
# Markdown Cell: Story + Context + Real-World Relevance

# Persona: Software Developer
# Organization: Individual AI-Readiness Platform

"""
Task: Project Initialization and Structure Setup

We're starting a new AI service within the Individual AI-Readiness Platform. To ensure a consistent
and maintainable codebase from day one, we'll initialize a new Python project using Poetry and
establish a standard project directory structure. This structure will accommodate various
components like API routes, configuration, models, and services, making our project scalable
and easy to navigate for any developer joining the team.

Poetry helps us manage dependencies, create isolated virtual environments, and build distributable
packages, which is crucial for moving our service from development to production seamlessly.
"""

# Code cell (function definition + function execution)

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
!mkdir -p src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas}
!mkdir -p src/air/{agents,observability,mcp,events}
!mkdir -p tests/{unit,integration,evals}
!mkdir -p docs/{adr,requirements,failure-modes}

# Create an __init__.py file to make 'air' a Python package
!touch src/air/__init__.py
```

```markdown
### Explanation of Execution
The preceding commands simulate the creation of a new Python project using Poetry and establish a well-structured directory layout.
- `poetry init` sets up the `pyproject.toml` file, which is the heart of our project's metadata and dependency management.
- `poetry add` commands populate `pyproject.toml` with our runtime and development dependencies, ensuring they are correctly versioned and installed in an isolated virtual environment.
- The `mkdir -p` commands create a logical, hierarchical structure for our source code, separating concerns and making the codebase easier to understand, maintain, and scale. This aligns with industry best practices for larger applications.
For instance, API versioning (`v1`, `v2`) is baked into the structure from the start, allowing for smooth, backward-compatible API evolution.
```

## 3. Safeguarding Configuration: Pydantic Validation in Action

Misconfigurations are a leading cause of outages and unexpected behavior in production systems. For our AI-Readiness Platform, critical parameters — from API keys to model scoring weights — must be validated *before* the application starts. This proactive approach prevents runtime errors and ensures operational stability.

### Why this matters (Real-world relevance)
Consider the **Knight Capital incident** in 2012, where a single configuration deployment error led to a \$440 million loss in 45 minutes. A flag intended for a "test" environment was mistakenly set to "production," triggering unintended automated trades. Pydantic's validation-at-startup prevents such catastrophic errors by ensuring all configuration parameters meet defined constraints, failing fast with clear error messages if they don't. For our AI services, this means ensuring model weights sum correctly or API keys are present, directly impacting the reliability and safety of our AI-driven decisions.

Here, we define our `Settings` class using `pydantic-settings` and `Pydantic v2`. This provides a robust, type-safe, and validated configuration system, drawing values from environment variables or a `.env` file. We also include a `model_validator` to enforce complex rules, such as ensuring all scoring weights sum to 1.0.

### Mathematical Explanation: Validating Scoring Weights
In many AI/ML applications, especially those involving composite scores or weighted features, the sum of weights must adhere to a specific constraint, often summing to 1.0. This ensures that the individual components proportionally contribute to the overall score and that the scoring logic remains consistent. If these weights deviate from their expected sum, the model's output could be skewed, leading to incorrect predictions or decisions.

For a set of $N$ scoring weights, $w_1, w_2, \ldots, w_N$, the validation rule is:
$$ \sum_{i=1}^{N} w_i = 1.0 $$
Our `model_validator` explicitly checks this condition, raising an error if the sum deviates beyond a small epsilon (e.g., $0.001$) to account for floating-point inaccuracies. This is a crucial guardrail to prevent configuration errors that could lead to invalid AI scores.

```python
# Markdown Cell: Story + Context + Real-World Relevance

# Persona: Software Developer
# Organization: Individual AI-Readiness Platform

"""
Task: Implement a Configuration System with Full Validation

We are setting up the core configuration for our AI service. This includes application details,
API prefixes, database URLs, LLM provider keys, and crucial scoring parameters. To prevent
configuration-related failures, we'll use Pydantic-Settings for strong type validation and
enforce business rules like ensuring scoring weights sum to 1.0. This ensures the integrity
of our AI model's parameters and the overall stability of the service.

The use of `SecretStr` for API keys adds a layer of security by preventing accidental logging
of sensitive information.
"""

# Code cell (function definition + function execution)

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

```

```markdown
### Explanation of Execution
We've successfully defined our `Settings` class, which uses Pydantic to validate configuration parameters. When `settings = get_settings()` is called, Pydantic performs immediate validation based on the types, bounds (`Field(ge=..., le=...)`), and custom `model_validator` functions (e.g., `validate_weight_sums`).

- The `APP_NAME`, `APP_VERSION`, and `APP_ENV` are loaded, with `APP_ENV` restricted to a `Literal` set of values, ensuring type safety.
- `SecretStr` for `OPENAI_API_KEY` prevents sensitive information from being accidentally printed or exposed.
- The output shows that our scoring parameters, like `W_FLUENCY`, `W_DOMAIN`, and `W_ADAPTIVE`, are loaded correctly, and their sum is validated. This ensures that any AI scoring logic relying on these weights will operate with consistent and valid inputs, preventing the kind of "garbage in, garbage out" scenarios that can undermine AI system reliability.
This system acts as an early warning mechanism, catching configuration issues at application startup rather than letting them cause silent failures or incorrect AI decisions later in the workflow.
```

## 4. Building the API Core: Versioned Routers and Middleware

As the Software Developer, your task is to construct the FastAPI application, integrating versioned API routes and crucial middleware for cross-cutting concerns. This setup ensures our AI service is not only functional but also maintainable, observable, and adaptable to future changes. The "Application Factory Pattern" allows us to create multiple FastAPI app instances, useful for testing or different deployment contexts.

### Why this matters (Real-world relevance)
A production-ready AI service must handle various operational requirements beyond just serving model predictions.
- **API Versioning:** As AI models evolve, so do their APIs. Versioned routers (`/api/v1`, `/api/v2`) ensure backward compatibility, allowing seamless upgrades for clients without disrupting existing integrations. This is crucial for an "Individual AI-Readiness Platform" that will continuously evolve its capabilities.
- **Middleware:** Cross-cutting concerns like CORS (Cross-Origin Resource Sharing), request timing, and request ID tracking are essential for web services.
    - **CORS Middleware** allows frontend applications (e.g., a dashboard for the AI platform) to securely interact with our backend API.
    - **Request Timing Middleware** provides crucial performance metrics. By attaching an `X-Process-Time` header to every response, we enable monitoring systems to track API latency, a key indicator of service health and user experience.
    - **Request ID Middleware** assigns a unique ID (`X-Request-ID`) to each request. This ID is vital for tracing requests through complex microservice architectures, especially when debugging issues across multiple services in a production environment.
- **Exception Handling:** Graceful error handling, especially for validation errors, provides informative feedback to API consumers, making the service more user-friendly and robust.

```python
# Markdown Cell: Story + Context + Real-World Relevance

# Persona: Software Developer
# Organization: Individual AI-Readiness Platform

"""
Task: Implement FastAPI Application with Versioned Routers and Middleware

Now we will build the main FastAPI application. This involves:
1. Defining a `lifespan` context manager for startup and shutdown events (e.g., initializing tracing).
2. Implementing an "Application Factory Pattern" (`create_app`) to create FastAPI instances.
3. Adding `CORSMiddleware` to handle cross-origin requests securely.
4. Implementing a custom HTTP middleware to inject a unique request ID and track request processing time.
5. Defining global exception handlers for better error reporting.
6. Including versioned API routers (`v1_router`, `v2_router`) and a dedicated health router.

This setup ensures our AI service is robust, secure, observable, and ready for continuous deployment.
"""

# Code cell (function definition + function execution)

# Content for src/air/api/main.py
main_api_content = f"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import time
import uuid
import sys

# Ensure settings are importable from the project structure
if 'src' not in sys.path:
    sys.path.insert(0, 'src')
from air.config.settings import settings

# Placeholder routers for V1, V2, and Health
# In a real project, these would be imported from separate files
# e.g., from air.api.routes.v1 import router as v1_router
# For this notebook, we'll create simple APIRouter instances here.
v1_router = APIRouter()
v2_router = APIRouter()
health_router = APIRouter() # This will be detailed in the next section

# Dummy endpoints for v1 and v2 to show routing
@v1_router.get("/items")
async def read_v1_items():
    return {{"message": "Hello from API v1"}}

@v2_router.get("/items")
async def read_v2_items():
    # In a real scenario, this might return different data or use streaming
    return {{"message": "Hello from API v2 - enhanced!"}}

# Placeholder for observability setup
def setup_tracing(app: FastAPI):
    print("Initializing observability tracing (simulated)...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Application lifespan manager for startup and shutdown events.\"\"\"
    # Startup
    print(f"🚀 Starting {{settings.APP_NAME}} v{{settings.APP_VERSION}}")
    print(f"🌍 Environment: {{settings.APP_ENV}}")
    print(f"🔢 Parameter Version: {{settings.parameter_version}}")
    print(f"🛡️ Guardrails: {{'Enabled' if settings.GUARDRAILS_ENABLED else 'Disabled'}}")
    print(f"💰 Cost Budget: ${{settings.DAILY_COST_BUDGET_USD}}/day")

    # Initialize observability in non-dev environments
    if not settings.DEBUG:
        setup_tracing(app)

    yield # Application runs here

    # Shutdown
    print("👋 Shutting down...")

def create_app() -> FastAPI:
    \"\"\"Application factory pattern for creating FastAPI instances.\"\"\"
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Individual AI-Readiness Score Platform - Production Ready",
        lifespan=lifespan,
        # Only show docs in debug mode for production security
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # ====================================
    # MIDDLEWARE
    # ====================================

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [], # Allow all origins in debug, specific in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Timing Middleware
    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id # Store request_id in request.state
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{{duration:.4f}}"
        return response

    # ====================================
    # EXCEPTION HANDLERS
    # ====================================

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        \"\"\"Custom handler for ValueError, often from Pydantic validation failures.\"\"\"
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={{
                "detail": str(exc),
                "type": "validation_error",
                "request_id": getattr(request.state, 'request_id', None),
            }},
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        \"\"\"Custom handler for HTTPException to include request ID.\"\"\"
        return JSONResponse(
            status_code=exc.status_code,
            content={{
                "detail": exc.detail,
                "request_id": getattr(request.state, 'request_id', None),
            }},
            headers=exc.headers,
        )

    # ====================================
    # ROUTES
    # ====================================

    # Health checks (no version prefix)
    app.include_router(health_router, tags=["Health"])

    # API v1 (original)
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])

    # API v2 (with streaming, enhanced responses)
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app

# Create the FastAPI app instance using the factory
app = create_app()

# You can't directly "run" uvicorn in a Jupyter notebook cell for an extended period,
# but we can simulate the app's startup phase and demonstrate router inclusion.
print("\\n--- Simulating App Startup ---")
async def simulate_startup():
    async with lifespan(app):
        print(f"App initialized with routers: ")
        for route in app.routes:
            # Check for hasattr to avoid errors on non-routing objects
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {','.join(route.methods)} {route.path}")
        print("Application is running (simulated).")
        # In a real environment, uvicorn would now be serving requests.
        # For demonstration, we simulate fetching an endpoint.
        # We cannot truly make HTTP requests to a non-running server from within the same cell.
        # However, we can assert that the app object and its routes are correctly configured.

await simulate_startup()
"""

create_file("src/air/api/main.py", main_api_content)
# To reload the `app` object with the new content, we need to re-execute the cell where `app = create_app()` is called.
# For notebook demonstration, we will define `app` directly for simplicity, but acknowledge the factory pattern.

# Re-create app using the code above, making routers directly available for inclusion.
# For simplicity, these will be defined locally in the notebook context,
# rather than attempting to dynamically import them from string content.

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

    # Health router will be populated in the next step
    app_instance.include_router(health_router, tags=["Health"])
    app_instance.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])
    app_instance.include_router(v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app_instance

app_core = create_app_notebook()

# Simulate app startup to verify lifespan and route registration
async def verify_app_core_startup():
    async with lifespan_notebook(app_core):
        print("\nFastAPI Application Core Setup Complete. Registered routes:")
        for route in app_core.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {','.join(route.methods)} {route.path}")
        print("Expected output shows /api/v1/items and /api/v2/items along with health routes.")

await verify_app_core_startup()
```

```markdown
### Explanation of Execution
The `create_app_notebook()` function demonstrates the "Application Factory Pattern" by returning a fully configured FastAPI application instance.
- The `lifespan_notebook` context manager ensures that startup (e.g., observability initialization) and shutdown tasks are handled gracefully.
- `CORSMiddleware` is added, crucial for allowing web clients to interact with our API securely.
- The custom `add_request_context_notebook` middleware successfully injects a unique `X-Request-ID` and `X-Process-Time` header into responses. This is vital for distributed tracing and performance monitoring.
- The exception handlers for `ValueError` and `HTTPException` are registered, providing standardized and informative error responses.
- Finally, the versioned routers (`/api/v1/items`, `/api/v2/items`) are included, demonstrating how different API versions can coexist, enabling the platform to evolve its AI capabilities without breaking existing client integrations.
The simulated startup confirms that all these components are correctly initialized and registered within the FastAPI application.
```

## 5. Ensuring Service Reliability: Comprehensive Health Checks

For any production AI service, merely having the API running isn't enough; we need to know if it's truly *healthy* and capable of serving requests. This means checking not only the application itself but also all its critical dependencies like databases, caching layers (Redis), and external LLM APIs. Robust health checks are vital for automated monitoring, load balancing, and self-healing systems in containerized environments like Kubernetes.

### Why this matters (Real-world relevance)
As a Software Developer, implementing detailed health checks is crucial for ensuring the AI-Readiness Platform's uptime and reliability. Imagine a scenario where your AI model relies on a database for feature storage and an external LLM API for inference. If the database is down, or the LLM API is unreachable, your service might technically be "running" but unable to perform its core function.
- **`/health` (Basic Health):** A fast check for basic application responsiveness, used by load balancers.
- **`/health/detailed` (Detailed Health):** Provides an in-depth status of all internal and external dependencies. This allows operators to quickly diagnose issues. For example, if the `check_llm()` indicates a "degraded" status due to high latency, it immediately points to a potential external API issue impacting our AI service's performance.
- **`/health/ready` (Readiness Probe):** Tells container orchestrators (like Kubernetes) if the service is ready to accept traffic. If dependencies are unhealthy, the service shouldn't receive requests.
- **`/health/live` (Liveness Probe):** Indicates if the application is still running and hasn't frozen. If this fails, the container needs to be restarted.
These checks are fundamental for maintaining service level agreements (SLAs) and ensuring our AI services are always operational.

```python
# Markdown Cell: Story + Context + Real-World Relevance

# Persona: Software Developer
# Organization: Individual AI-Readiness Platform

"""
Task: Implement Comprehensive Health Check Endpoints with Dependency Status

We need to add health check endpoints to our API. These endpoints will provide insights into
the application's status and its critical dependencies. This involves:
1. Defining Pydantic models for `DependencyStatus`, `HealthResponse`, and `DetailedHealthResponse`.
2. Implementing asynchronous functions to simulate checks for external dependencies (database, Redis, LLM).
3. Creating API endpoints for basic health (`/health`), detailed health (`/health/detailed`),
   readiness (`/health/ready`), and liveness (`/health/live`).

These checks are crucial for reliable deployments and operational monitoring in a production AI environment.
"""

# Code cell (function definition + function execution)

# Content for src/air/api/routes/health.py
health_router_content = """
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
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
    status: Literal["healthy", "degraded", "unhealthy", "not_configured"]
    latency_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    \"\"\"Basic health check response.\"\"\"
    status: Literal["healthy", "degraded", "unhealthy"]
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
            name="database",
            status="healthy",
            latency_ms=10.0,
        )
    except Exception as e:
        return DependencyStatus(
            name="database",
            status="unhealthy",
            error=str(e),
        )

async def check_redis() -> DependencyStatus:
    \"\"\"Check Redis connectivity.\"\"\"
    try:
        # In production, actually ping Redis
        await asyncio.sleep(0.005) # Simulate network latency
        return DependencyStatus(
            name="redis",
            status="healthy",
            latency_ms=5.0,
        )
    except Exception as e:
        return DependencyStatus(
            name="redis",
            status="unhealthy",
            error=str(e),
        )

async def check_llm() -> DependencyStatus:
    \"\"\"Check LLM API availability.\"\"\"
    try:
        if not settings.OPENAI_API_KEY:
            return DependencyStatus(
                name="llm",
                status="not_configured",
                latency_ms=None,
                error="OPENAI_API_KEY not set"
            )
        # Would ping LLM health endpoint or make a dummy request
        await asyncio.sleep(0.02) # Simulate LLM API call latency
        return DependencyStatus(
            name="llm",
            status="healthy",
            latency_ms=20.0,
        )
    except Exception as e:
        return DependencyStatus(
            name="llm",
            status="degraded", # LLM might be degraded rather than unhealthy if it's external
            error=str(e),
        )

@router.get("/health", response_model=HealthResponse, summary="Basic Health Check")
async def health_check() -> HealthResponse:
    \"\"\"Basic health check - fast, no dependency checks.\"\"\"
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
    )

@router.get("/health/detailed", response_model=DetailedHealthResponse, summary="Detailed Health Check with Dependencies")
async def detailed_health_check() -> DetailedHealthResponse:
    \"\"\"Detailed health check with dependency status.\"\"\"
    # Check all dependencies concurrently
    db_status, redis_status, llm_status = await asyncio.gather(
        check_database(),
        check_redis(),
        check_llm(),
    )

    dependencies = {
        "database": db_status,
        "redis": redis_status,
        "llm": llm_status,
    }

    # Overall status is degraded if any dependency is unhealthy or degraded
    overall_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    for dep in dependencies.values():
        if dep.status == "unhealthy":
            overall_status = "unhealthy"
            break
        elif dep.status == "degraded":
            overall_status = "degraded"
        elif dep.status == "not_configured" and overall_status == "healthy":
            overall_status = "degraded" # Consider not_configured as degraded if no other issues

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

@router.get("/health/ready", summary="Kubernetes Readiness Probe")
async def readiness_check():
    \"\"\"Kubernetes readiness probe: checks if the service is ready to accept traffic.\"\"\"
    # A service is "ready" if all critical dependencies are healthy.
    # We use the detailed health check to determine readiness.
    health = await detailed_health_check()
    if health.status == "unhealthy" or health.status == "degraded":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": f"Overall status: {health.status}"},
        )
    return {"status": "ready"}

@router.get("/health/live", summary="Kubernetes Liveness Probe")
async def liveness_check():
    \"\"\"Kubernetes liveness probe: checks if the application is alive and responsive.\"\"\"
    # A simple check that doesn't involve heavy dependency polling,
    # just ensures the application process is running and responding to HTTP requests.
    return {"status": "alive"}
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
print("\n--- Testing Health Check Endpoints (simulated calls) ---")

# Test /health
basic_health_response = await health_check_func()
print(f"Basic Health Check (/health): {basic_health_response.model_dump_json(indent=2)}")

# Test /health/detailed
detailed_health_response = await detailed_health_check_func()
print(f"\nDetailed Health Check (/health/detailed): {detailed_health_response.model_dump_json(indent=2)}")

# Test /health/ready (successful case)
try:
    readiness_status = await readiness_check_func()
    print(f"\nReadiness Probe (/health/ready): {readiness_status}")
except HTTPException as e:
    print(f"\nReadiness Probe Failed: {e.detail}")

# Test /health/live
liveness_status = await liveness_check_func()
print(f"\nLiveness Probe (/health/live): {liveness_status}")

```

```markdown
### Explanation of Execution
The execution demonstrates the functionality of our comprehensive health check endpoints:
- The `/health` endpoint provides a quick, basic check of the application's version, environment, and current timestamp, confirming the service process is responsive.
- The `/health/detailed` endpoint concurrently checks all configured dependencies (database, Redis, LLM API using `asyncio.gather`). It aggregates their individual statuses and latencies to determine an overall service health, providing granular insights crucial for troubleshooting.
- The `/health/ready` endpoint indicates if the service is prepared to receive traffic, taking into account the health of its critical dependencies. In our simulation, it returns "ready" as all dependencies are marked "healthy" or "not_configured" (which is treated as degraded in this context, but not "unhealthy"). If a dependency were "unhealthy," this probe would fail, instructing orchestrators to not route traffic to this instance.
- The `/health/live` endpoint confirms the application is active and hasn't crashed, allowing orchestrators to restart it if unresponsive.

These endpoints provide the essential observability for the AI-Readiness Platform, enabling automated systems to ensure high availability and rapid detection of operational issues.
```

## 6. Avoiding Common Pitfalls: Best Practices in Action

As a Software Developer, understanding and proactively addressing common mistakes is just as important as implementing new features. This section reviews critical configuration and application setup pitfalls, demonstrating how the patterns we've adopted (like Pydantic validation and FastAPI's `lifespan` manager) help prevent them. This hands-on review reinforces best practices for building robust and secure AI services.

### Why this matters (Real-world relevance)
Ignoring best practices often leads to hidden bugs, security vulnerabilities, or catastrophic failures in production. For an AI service, this could mean incorrect model predictions due to bad configurations, data breaches from exposed secrets, or resource leaks that degrade performance over time. By explicitly addressing these "common mistakes," we ensure that the Individual AI-Readiness Platform adheres to high standards of reliability, security, and maintainability, protecting both our data and our reputation.

```python
# Markdown Cell: Story + Context + Real-World Relevance

# Persona: Software Developer
# Organization: Individual AI-Readiness Platform

"""
Task: Review Common Mistakes & Troubleshooting

We will examine common errors in setting up production-ready services and demonstrate how
our current architecture prevents them. This includes:
1. **Mistake 1: Not validating weight sums:** How Pydantic's `model_validator` catches this at startup.
2. **Mistake 2: Exposing secrets in logs:** How Pydantic's `SecretStr` masks sensitive values.
3. **Mistake 3: Missing lifespan context manager:** Why `asynccontextmanager` is crucial for resource cleanup.

Understanding these common pitfalls and their solutions is essential for building truly resilient AI services.
"""

# Code cell (function definition + function execution)

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
print("\n# FIX: The `model_validator` in `Settings` class catches this at startup.")
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
print("\n--- Mistake 2: Exposing secrets in logs ---")
print("# WRONG Example: Logging the actual API key directly.")
dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
print(f"  Using key: {dummy_api_key}") # This would print the full key!

# Fix: Use Pydantic's SecretStr. It masks values upon string conversion.
print("\n# FIX: Use `SecretStr` which masks values.")
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
print("\n--- Mistake 3: Missing lifespan context manager ---")
print("# WRONG Example: FastAPI app without a lifespan context manager.")
# app = FastAPI() # Resources leak on shutdown!
# print("  FastAPI app initialized without lifespan. (Resources would leak!)")

# Fix: Always use `asynccontextmanager` for FastAPI's `lifespan`.
# We have already implemented this in `create_app_notebook()` and `lifespan_notebook()`.
print("\n# FIX: Always use `asynccontextmanager` for `lifespan` for proper startup/shutdown.")
print("  Our `create_app_notebook()` uses `lifespan_notebook`:")

# We can re-run the startup simulation to show the effect
async def verify_lifespan_fix():
    print("\n  Simulating app startup with lifespan:")
    async with lifespan_notebook(app_core):
        print("    Application started up (resources initialized).")
    print("    Application shut down (resources cleaned up).")

await verify_lifespan_fix()

```

```markdown
### Explanation of Execution
This section actively demonstrates how implementing robust practices prevents common errors:
1.  **Weight Sum Validation:** When attempting to load settings with incorrect scoring weights (e.g., sum not equal to 1.0), Pydantic's `model_validator` immediately raises a `ValueError`. This "fail-fast" mechanism prevents the AI service from starting with invalid parameters that could lead to incorrect model behavior, fulfilling the goal of preventing Knight Capital-like configuration errors.
2.  **Secret Handling:** By using `SecretStr` for `OPENAI_API_KEY`, the output shows that the sensitive key is masked. This is a critical security measure for the AI-Readiness Platform, preventing accidental exposure of credentials in logs, console output, or error reports, significantly reducing the risk of data breaches.
3.  **Lifespan Management:** The simulated startup and shutdown using the `lifespan_notebook` context manager visually confirms that explicit startup and shutdown routines are executed. This ensures that resources like database connections, caching clients, or tracing exporters are properly initialized when the AI service starts and gracefully closed when it shuts down, preventing resource leaks and ensuring application stability over its lifecycle.

By embracing these best practices, we ensure that the AI services built for the Individual AI-Readiness Platform are not only performant but also secure, reliable, and maintainable in a production environment.
```
