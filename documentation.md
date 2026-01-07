id: 695eb69866ad0b4a256fa7c4_documentation
summary: Foundation & Platform Setup Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Foundation and Platform Setup for InnovateAI

## 1. Introduction to QuLab: Foundation & Platform Setup
Duration: 0:10

InnovateAI Solutions is developing a new AI platform called "Predictive Intelligence Engine" (PIE) that will offer various AI services through a unified API. Alex, a Senior Software Engineer at InnovateAI Solutions, has been tasked with establishing a robust, maintainable, and scalable backend foundation for PIE. This involves setting up the project structure, defining a resilient configuration system, and scaffolding the core FastAPI application with essential features like middleware and API versioning. The ultimate goal is to ensure the platform can evolve gracefully and reliably as new AI models and services are integrated. This lab will guide you through Alex's workflow, demonstrating how to apply modern Python development practices to create a solid foundation for a production AI application.

The importance of this application lies in creating a highly reliable, scalable, and maintainable AI platform. By focusing on robust configuration, clear API versioning, and production-grade deployment strategies, developers can avoid common pitfalls and ensure their AI services can grow and adapt with evolving business needs and technological advancements. This foundation is critical for any AI initiative aiming for long-term success and broad adoption.

### Key Objectives

| Bloom's Level | Objective |
| : | :-- |
| Remember | List the components of a FastAPI application |
| Understand | Explain why Pydantic validation prevents configuration errors |
| Apply | Implement a configuration system with weight validation |
| Create | Design a project structure for production AI platforms |

### Tools Introduced

| Tool | Purpose | Why This Tool |
| :- | :- | : |
| Python 3.12 | Runtime | Pattern matching, performance improvements |
| Poetry | Dependency management| Lock files, virtual environments |
| FastAPI | Web framework | Async support, automatic OpenAPI |
| Pydantic v2 | Validation | Type safety, settings management |
| Docker | Containerization | Reproducible environments |

### Key Concepts

*   Application factory pattern
*   Configuration validation with constraints
*   Middleware stacks (CORS, timing, error handling)
*   Health check endpoints
*   API versioning foundations

### Prerequisites

*   Python proficiency (functions, classes, async/await)
*   Basic command line usage
*   Understanding of REST APIs

### Time Estimate

| Activity | Duration |
| :-- | :- |
| Lecture | 1 hour |
| Lab Work | 3 hours |
| Challenge Extensions | +2 hours |
| **Total** | **6 hours**|

### 1.1 Objectives

| Objective | Description | Success Criteria |
| :- | :-- | :- |
| Repository Setup | Initialize monorepo with Poetry | `poetry install` succeeds |
| Configuration | Pydantic settings with validation | All parameters validated |
| API Scaffold | FastAPI with middleware stack | `/health` returns 200 |
| Docker Setup | Containerized development | `docker-compose up` works |
| CI Pipeline | GitHub Actions workflow | Tests pass in CI |
| API Versioning | Version prefix structure | v1/v2 routers ready |

## 2. Project Initialization and Monorepo Structure with Poetry
Duration: 0:20

Alex knows that a well-organized project structure is paramount for scalability and team collaboration, especially for a platform that will eventually host multiple AI services (a "monorepo" style). He opts for Poetry to manage dependencies and virtual environments, ensuring consistency across development, staging, and production environments. The directory structure is designed to separate concerns: API routes, configuration, models, services, and schemas are logically grouped.

### Project Directory Structure

Below is the conceptual directory structure for the `individual-air-platform`. This layout separates the core application logic (`src/air`), API versions (`src/air/api/routes/v1`, `v2`), and other concerns like configuration, models, services, and test suites.

```
individual-air-platform/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── air/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py        (FastAPI application entry point)
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── v1/
│       │       │   └── __init__.py  (API v1 endpoints)
│       │       └── v2/
│       │           └── __init__.py  (API v2 endpoints)
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py    (Pydantic settings)
│       ├── models/
│       │   └── __init__.py    (Pydantic models for data)
│       ├── services/
│       │   └── __init__.py    (Business logic services)
│       ├── schemas/
│       │   └── __init__.py    (API request/response schemas)
│       ├── agents/
│       │   └── __init__.py    (AI agents, if applicable)
│       ├── observability/
│       │   └── __init__.py    (Logging, monitoring)
│       ├── mcp/
│       │   └── __init__.py    (Main Control Plane logic)
│       └── events/
│           └── __init__.py    (Event handling)
└── tests/
    ├── unit/
    ├── integration/
    └── evals/
```

### Conceptual Commands for Project Setup

Here are the commands Alex would execute to set up the project and its dependencies using Poetry:

```bash
# Create project root directory and navigate into it
mkdir individual-air-platform && cd individual-air-platform

# Initialize Poetry project
poetry init --name="individual-air-platform" --python="^3.12"

# Install Week 1 dependencies (production dependencies)
poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette

# Install Development dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy

# Create the source directory structure
mkdir -p src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas}
mkdir -p src/air/{agents,observability,mcp,events}
mkdir -p tests/{unit,integration,evals}

# Create __init__.py files to make directories Python packages
touch src/air/__init__.py
touch src/air/api/__init__.py
touch src/air/api/routes/__init__.py
touch src/air/api/routes/v1/__init__.py
touch src/air/api/routes/v2/__init__.py
touch src/air/config/__init__.py
touch src/air/models/__init__.py
touch src/air/services/__init__.py
touch src/air/schemas/__init__.py
touch src/air/agents/__init__.py
touch src/air/observability/__init__.py
touch src/air/mcp/__init__.py
touch src/air/events/__init__.py
```

<aside class="positive">
  <b>Why Poetry?</b> Poetry simplifies dependency management by providing a single tool to handle project creation, dependency installation, and virtual environment management. It generates a `poetry.lock` file that ensures deterministic builds, crucial for production deployments.
</aside>

## 3. Robust Configuration with Pydantic v2
Duration: 0:30

One of the most critical aspects of any production application is its configuration management. Alex, having dealt with numerous bugs due to incorrect environment variables or misconfigured parameters, chooses Pydantic v2 for this task. Pydantic provides robust validation, type checking, and the ability to load settings from various sources (like environment variables or `.env` files). This ensures that the application starts only with valid configurations, preventing runtime errors.

A key requirement for the "Predictive Intelligence Engine" involves dynamic scoring parameters for AI models. For instance, specific weights for model components (e.g., fluency, domain relevance, adaptiveness) must sum to 1.0 to ensure a consistent scoring scale. Alex implements a Pydantic `model_validator` to enforce this business logic.

The `model_config` `SettingsConfigDict` is used to specify how settings are loaded (e.g., from `.env` files, case insensitivity). Sensitive information, like API keys, is handled with `SecretStr` to prevent accidental logging or exposure.

The formula for validating component weights is:
$$ W_{fluency} + W_{domain} + W_{adaptive} = 1.0 $$
where $W_{fluency}$ is the weight for the fluency component, $W_{domain}$ is the weight for the domain expertise component, and $W_{adaptive}$ is the weight for the adaptiveness component.

This equation ensures that the individual contributions of different AI model aspects (fluency, domain relevance, adaptability) are correctly normalized and collectively account for the total score, preventing miscalibration of the model's output. If the sum deviates significantly, for example, $abs(W_{sum} - 1.0) > 0.001$, a `ValueError` is raised, indicating an "invalid configuration".

### Pydantic Settings Implementation (`src/air/config/settings.py`)

```python
import os
from typing import Literal, Optional
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    '''Application settings with comprehensive validation.'''

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
        '''
        Validate that the component weights for the V^R scoring model sum to 1.0.
        This ensures correct normalization and consistency in scoring.
        '''
        vr_sum = self.W_FLUENCY + self.W_DOMAIN + self.W_ADAPTIVE
        if abs(vr_sum - 1.0) > 0.001:
            raise ValueError(f"V^R weights must sum to 1.0. Got {vr_sum:.2f} (W_FLUENCY={self.W_FLUENCY}, W_DOMAIN={self.W_DOMAIN}, W_ADAPTIVE={self.W_ADAPTIVE})")
        return self

@lru_cache
def get_settings() -> Settings:
    '''Cached function to get application settings.'''
    return Settings()
```

### Configuration Validation Flow

This diagram illustrates how Pydantic's `Settings` class and custom `model_validator` ensure configuration integrity:

```
++
|   Load Configuration      |
| (.env file, Environment   |
|         Variables)        |
++
             ↓
++
|    Pydantic Settings      |
|      (BaseSettings)       |
++
             ↓
++
|      Field Validation     |
| (Type checking, min/max   |
|   constraints for each    |
|        parameter)         |
++
             ↓
++
|  Custom `model_validator` |
| (`validate_weight_sums`)  |
++
             ↓
++
| Weights Sum to 1.0?       |
| (abs(W_sum - 1.0) < 0.001)|
+--++
   YES ↓         NO ↓
++   +--+
| Valid   |   | ValueError:  |
|Settings |   | Invalid Config|
++   +--+
```

<aside class="negative">
  <b>Warning:</b> Incorrectly configured weights in an AI model can lead to skewed results, misclassification, and unreliable predictions. The Pydantic validator is crucial for catching these errors early.
</aside>

## 4. Building the FastAPI Application Core with Middleware
Duration: 0:30

Now that the project structure and configuration system are in place, Alex moves on to scaffolding the core FastAPI application. He needs to define the main application entry point (`main.py`) and incorporate essential features for a production-grade API:

1.  **Application Lifespan Management:** Using FastAPI's `lifespan` context manager ensures that startup tasks (e.g., database connections, caching initialization) and shutdown tasks (e.g., closing connections, resource cleanup) are handled gracefully. This prevents resource leaks and ensures a clean application lifecycle.
2.  **CORS Middleware:** For web applications that might call the API from different domains, Cross-Origin Resource Sharing (CORS) is essential for security and interoperability. `CORSMiddleware` handles the necessary HTTP headers to allow or restrict access.
3.  **Custom Request Timing Middleware:** To monitor performance and aid in debugging, Alex implements a custom middleware that measures the processing time for each request and adds a unique request ID. This provides valuable observability without cluttering the main business logic.

These foundational elements are critical for building a reliable and observable API.

### FastAPI Application Core (`src/air/api/main.py`)

```python
import os
import asyncio
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware

# Assuming settings are imported from a module like src.air.config.settings
# For this codelab, settings is globally available as provided in the initial app.py
from src.air.config.settings import get_settings
settings = get_settings()

# Define simple routers for demonstration
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
    """
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.APP_ENV} environment...")
    await asyncio.sleep(0.05)
    print("✨ Application startup complete: Database connections, cache initialized.")
    yield # This is where the application would run
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

    #  Middleware Stack 

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [], # Allow all origins in debug, restrict in prod
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

    #  API Routes 

    app.include_router(health_router, tags=["Health"])

    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX)

    return app

# Example of how to run the app using Uvicorn (not part of Streamlit, for context)
# if __name__ == "__main__":
#     import uvicorn
#     app_instance = create_app()
#     uvicorn.run(app_instance, host="0.0.0.0", port=8000)
```

### FastAPI Request Processing Flow

This diagram illustrates how requests pass through the FastAPI application, interacting with middleware before reaching route handlers:

```
+--+
|    Client Request     |
| (e.g., GET /api/v1/status) |
+--+
            ↓
+--+
|    FastAPI Application|
|   (create_app())      |
+--+
            ↓
+--+
|    CORSMiddleware     |
| (Handles Cross-Origin |
|       requests)       |
+--+
            ↓
+--+
|  Custom Request Timing|
|       Middleware      |
| (Adds X-Request-ID,   |
| Measures X-Process-Time)|
+--+
            ↓
+--+
|     Route Handler     |
| (e.g., get_v1_status  |
|   function for /api/v1/status)|
+--+
            ↓
+--+
|   Response from       |
|     Route Handler     |
+--+
            ↓
+--+
|  Custom Request Timing|
|       Middleware      |
| (Finalizes X-Process-Time|
|   adds headers to response)|
+--+
            ↓
+--+
|    CORSMiddleware     |
| (Adds CORS headers to |
|       response)       |
+--+
            ↓
+--+
|    Client Response    |
+--+
```

<aside class="positive">
  The <b>Application Factory Pattern</b> (using `create_app()`) is a best practice for building FastAPI applications. It makes the application more testable, reusable, and configurable, as you can create different instances of your app with varying configurations for different environments (e.g., testing, development, production).
</aside>

## 5. API Versioning for Scalability and Evolution
Duration: 0:15

Alex understands that AI models and service contracts evolve rapidly. To prevent breaking changes for existing users while simultaneously introducing new features or improved models, a clear API versioning strategy is crucial. By defining separate `APIRouter` instances for `v1` and `v2` and associating them with distinct URL prefixes (`/api/v1` and `/api/v2`), he ensures that different versions of the API can coexist. This allows InnovateAI Solutions to deprecate older versions gracefully and onboard new clients to improved interfaces without forcing immediate migrations. This separation is fundamental for maintaining backward compatibility and enabling agile development of new features.

The strategy employs **URI Versioning**, where the API version is embedded directly into the URL path, for example:
`https://api.innovateai.com/api/v1/predict`
where `/api/v1` denotes the first version of the API.
`https://api.innovateai.com/api/v2/predict`
where `/api/v2` denotes the second, potentially updated, version of the API.

This approach makes the version explicit and easily understandable by clients.

### Conceptual Implementation in `main.py`

The integration of versioned routers happens within the `create_app` function:

```python
# ... (within create_app() function in src/air/api/main.py) ...

    #  API Routes 
    # The health_router does not have a version prefix as it's a general endpoint
    app.include_router(health_router, tags=["Health"])

    # Include version 1 API routes with its dedicated prefix
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    # Include version 2 API routes with its dedicated prefix
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX)

    return app
```

This section confirms the logical separation of API versions. By conceptually demonstrating how `v1_router` and `v2_router` would be populated with version-specific endpoints, Alex has laid the groundwork for future API development. New features or breaking changes can be introduced in `v2` without impacting `v1` clients, providing a robust pathway for the PIE platform's growth and evolution. The health check endpoint ensures basic service availability can always be monitored.

## 6. Conceptualizing Containerization and CI/CD for Production Readiness
Duration: 0:20

Alex understands that for InnovateAI Solutions to deploy the "Predictive Intelligence Engine" reliably, containerization and a robust Continuous Integration/Continuous Deployment (CI/CD) pipeline are essential. These practices ensure that the application runs consistently across different environments and that code changes are automatically tested and validated.

**Containerization with Docker:** Docker provides isolated, portable environments for the application. This eliminates "it works on my machine" problems by packaging the application and all its dependencies into a single, deployable unit (a Docker image). Alex envisions a `Dockerfile` that builds the application image and a `docker-compose.yml` file for defining how the application services (e.g., FastAPI, database, Redis) run together in a local development environment.

**GitHub Actions Workflow:** For automated testing and quality assurance, Alex will set up a GitHub Actions workflow. This CI pipeline will automatically lint the code, run unit and integration tests, and check code coverage every time changes are pushed to the repository. This proactive approach catches bugs early, maintains code quality, and ensures that only validated code makes it to production.

While the full implementation of Dockerfiles and GitHub Actions YAMLs are beyond the scope of this initial setup (and are platform-specific deployment steps), Alex has conceptually planned for their integration. Their location and purpose are defined in the project's foundational thinking.

### Conceptualizing Production Infrastructure

**Containerization (Docker):**

Alex plans to create a `Dockerfile` in the project root (`./`) to define the application's runtime environment. This `Dockerfile` will specify the base Python image, install Poetry, add application code, and define the command to run the FastAPI application using Uvicorn.

For local development and multi-service orchestration, a `docker-compose.yml` file would be used to define how the FastAPI service, along with dependencies like PostgreSQL and Redis, run together in an isolated development environment.

Example conceptual files:
```text
.
├── Dockerfile
├── docker-compose.yml
└── ... (your project files)
```

**Continuous Integration (GitHub Actions):**

Alex will define a GitHub Actions workflow to automate testing and code quality checks. This workflow, typically located in `.github/workflows/ci.yml`, will execute tasks like:
*   Installing Python dependencies with Poetry.
*   Running `black` for consistent code formatting.
*   Running `ruff` for fast code linting.
*   Executing `pytest` for comprehensive unit and integration tests.
*   Checking code coverage with `pytest-cov` to ensure sufficient test coverage.

Example conceptual file:
```text
.
└── .github/
    └── workflows/
        └── ci.yml
```

These foundational steps, while not fully implemented here, are critical for ensuring the production-readiness, reliability, and maintainability of the AI platform.

## 7. Common Mistakes & Troubleshooting
Duration: 0:15

This section addresses common mistakes encountered when setting up a backend platform and how the design patterns covered in this lab mitigate them.

### Mistake 1: Weights don't sum to 1.0

**Problem:** AI model scoring weights (e.g., $W_{fluency}$, $W_{domain}$, $W_{adaptive}$) are configured incorrectly and do not sum to 1.0, leading to inaccurate or inconsistent model outputs.

```python
# WRONG (Example of incorrect configuration)
W_FLUENCY = 0.50
W_DOMAIN = 0.40
W_ADAPTIVE = 0.20 # Sum = 1.10! This will lead to an error.
```

**Fix:** The Pydantic `model_validator` in the `Settings` class catches this at application startup, preventing the application from running with invalid configuration. The interactive configuration section (Step 3: Robust Configuration with Pydantic v2) demonstrates this directly.

**Action:** Go back to **Step 3: Robust Configuration with Pydantic v2** and try entering `W_FLUENCY=0.50`, `W_DOMAIN=0.40`, and `W_ADAPTIVE=0.25` to see the validation error in action.

### Mistake 2: Exposing secrets in logs

**Problem:** Sensitive information like API keys is accidentally printed to logs or exposed in debugging interfaces, posing a security risk.

```python
# WRONG (Example of exposing a secret)
# If OPENAI_API_KEY was a simple str, this would print the raw key.
print(f"Using key: {settings.OPENAI_API_KEY}")
```

**Fix:** Use Pydantic's `SecretStr` type for sensitive fields. `SecretStr` automatically masks the value when printed, requiring an explicit call to `.get_secret_value()` to retrieve the raw string, thus preventing accidental exposure. The interactive configuration section (Step 3: Robust Configuration with Pydantic v2) demonstrates `SecretStr` behavior.

**Action:** Go back to **Step 3: Robust Configuration with Pydantic v2** and enter a simulated `OPENAI_API_KEY` to observe how it's masked by default. You can then check the "Show raw OpenAI API Key value" checkbox to see how to explicitly access the secret.

### Mistake 3: Missing lifespan context manager

**Problem:** Application resources (e.g., database connections, cache clients) are not properly initialized or cleaned up during startup and shutdown, leading to resource leaks, connection issues, or unstable behavior.

```python
# WRONG - No lifespan specified
app = FastAPI() # Resources might not be initialized or cleaned up properly
```

**Fix:** Always use FastAPI's `lifespan` context manager to define startup and shutdown logic. This ensures a controlled lifecycle for application resources. The **Step 4: Building the FastAPI Application Core with Middleware** page demonstrates the correct integration of `lifespan`.

**Action:** Go back to **Step 4: Building the FastAPI Application Core with Middleware** and click 'Simulate App Startup & Shutdown' to observe the correct lifespan management. This will show the startup and shutdown messages, simulating resource allocation and deallocation.
