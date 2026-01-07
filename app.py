
import streamlit as st
import os
import asyncio
import shutil
import time
import uuid
from typing import Literal, Optional
from functools import lru_cache
from contextlib import asynccontextmanager

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware

st.set_page_config(page_title="QuLab: Foundation & Platform Setup", layout="wide")
# Correct way to display image in sidebar:
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation & Platform Setup")
st.divider()

# --- Define Settings class and get_settings function directly in app.py ---
# This was previously assumed to be in 'source.py' but is required for interactive parts.

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

settings = get_settings() # Initialize settings globally for use in app.py

# --- Initialize session state variables ---
if 'page' not in st.session_state:
    st.session_state.page = "Overview"
if 'project_initialized' not in st.session_state:
    st.session_state.project_initialized = False
if 'w_fluency_input' not in st.session_state:
    st.session_state.w_fluency_input = 0.45
if 'w_domain_input' not in st.session_state:
    st.session_state.w_domain_input = 0.35
if 'w_adaptive_input' not in st.session_state:
    st.session_state.w_adaptive_input = 0.20
if 'openai_api_key_input' not in st.session_state:
    st.session_state.openai_api_key_input = ""
if 'show_raw_api_key' not in st.session_state:
    st.session_state.show_raw_api_key = False
if 'config_validation_output' not in st.session_state:
    st.session_state.config_validation_output = None
if 'current_settings_summary' not in st.session_state:
    st.session_state.current_settings_summary = ""
if 'fastapi_app_configured' not in st.session_state:
    st.session_state.fastapi_app_configured = False
if 'lifespan_log' not in st.session_state:
    st.session_state.lifespan_log = []

# --- Sidebar Navigation ---
st.sidebar.title("InnovateAI Platform Lab")
st.sidebar.markdown("---")

page_options = [
    "Overview",
    "1. Project Initialization",
    "2. Configuration System",
    "3. FastAPI Application Core",
    "4. API Versioning",
    "5. Production Readiness",
    "6. Troubleshooting"
]

# Handle navigation safely
try:
    current_index = page_options.index(st.session_state.page)
except ValueError:
    current_index = 0

page_selection = st.sidebar.selectbox(
    "Navigate Lab Sections",
    page_options,
    index=current_index,
    key="page_selector"
)
st.session_state.page = page_selection

# --- Main Content Area ---
if st.session_state.page == "Overview":
    st.header("✨ Lab Preamble")
    st.markdown(f"InnovateAI Solutions is developing a new AI platform called \"Predictive Intelligence Engine\" (PIE) that will offer various AI services through a unified API. Alex, a Senior Software Engineer at InnovateAI Solutions, has been tasked with establishing a robust, maintainable, and scalable backend foundation for PIE. This involves setting up the project structure, defining a resilient configuration system, and scaffolding the core FastAPI application with essential features like middleware and API versioning. The ultimate goal is to ensure the platform can evolve gracefully and reliably as new AI models and services are integrated. This lab will guide you through Alex's workflow, demonstrating how to apply modern Python development practices to create a solid foundation for a production AI application.")

    st.subheader("Key Objectives")
    st.markdown(
        """
        | Bloom's Level | Objective                                                 |
        | :------------ | :-------------------------------------------------------- |
        | Remember      | List the components of a FastAPI application              |
        | Understand    | Explain why Pydantic validation prevents configuration errors |
        | Apply         | Implement a configuration system with weight validation   |
        | Create        | Design a project structure for production AI platforms    |
        """
    )

    st.subheader("Tools Introduced")
    st.markdown(
        """
        | Tool        | Purpose              | Why This Tool                                  |
        | :---------- | :------------------- | :--------------------------------------------- |
        | Python 3.12 | Runtime              | Pattern matching, performance improvements     |
        | Poetry      | Dependency management| Lock files, virtual environments               |
        | FastAPI     | Web framework        | Async support, automatic OpenAPI               |
        | Pydantic v2 | Validation           | Type safety, settings management               |
        | Docker      | Containerization     | Reproducible environments                      |
        """
    )

    st.subheader("Key Concepts")
    st.markdown(
        """
        - Application factory pattern
        - Configuration validation with constraints
        - Middleware stacks (CORS, timing, error handling)
        - Health check endpoints
        - API versioning foundations
        """
    )

    st.subheader("Prerequisites")
    st.markdown(
        """
        - Python proficiency (functions, classes, async/await)
        - Basic command line usage
        - Understanding of REST APIs
        """
    )

    st.subheader("Time Estimate")
    st.markdown(
        """
        | Activity           | Duration |
        | :----------------- | :------- |
        | Lecture            | 1 hour   |
        | Lab Work           | 3 hours  |
        | Challenge Extensions | +2 hours |
        | **Total**          | **6 hours**|
        """
    )

    st.subheader("1.1 Objectives")
    st.markdown(
        """
        | Objective            | Description                       | Success Criteria                 |
        | :------------------- | :-------------------------------- | :------------------------------- |
        | Repository Setup     | Initialize monorepo with Poetry   | `poetry install` succeeds        |
        | Configuration        | Pydantic settings with validation | All parameters validated         |
        | API Scaffold         | FastAPI with middleware stack     | `/health` returns 200            |
        | Docker Setup         | Containerized development         | `docker-compose up` works        |
        | CI Pipeline          | GitHub Actions workflow           | Tests pass in CI                 |
        | API Versioning       | Version prefix structure          | v1/v2 routers ready              |
        """
    )

elif st.session_state.page == "1. Project Initialization":
    st.header("1. Project Initialization and Monorepo Structure with Poetry")
    st.markdown(f"Alex knows that a well-organized project structure is paramount for scalability and team collaboration, especially for a platform that will eventually host multiple AI services (a \"monorepo\" style). He opts for Poetry to manage dependencies and virtual environments, ensuring consistency across development, staging, and production environments. The directory structure is designed to separate concerns: API routes, configuration, models, services, and schemas are logically grouped.")
    st.markdown("### Commands to run (conceptual):")
    st.code(
        """
# Create project root directory and navigate into it
mkdir individual-air-platform && cd individual-air-platform

# Initialize Poetry project
poetry init --name="individual-air-platform" --python="^3.12"

# Install Week 1 dependencies
poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette

# Install Development dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy
        """,
        language="bash"
    )

    st.markdown("### Source Directory Structure")
    st.code(
        """
# Create source structure
mkdir -p src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas}
mkdir -p src/air/{agents,observability,mcp,events}
mkdir -p tests/{unit,integration,evals}
        """,
        language="bash"
    )

    def simulate_project_init_action():
        project_root = "individual-air-platform"
        if os.path.exists(project_root):
            shutil.rmtree(project_root)
        
        original_cwd = os.getcwd()
        
        try:
            os.makedirs(project_root, exist_ok=True)
            os.chdir(project_root)

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

            with open("src/air/__init__.py", "w") as f: pass
            for path in ["src/air/api", "src/air/api/routes", "src/air/api/routes/v1", "src/air/api/routes/v2",
                         "src/air/config", "src/air/models", "src/air/services", "src/air/schemas"]:
                with open(f"{path}/__init__.py", "w") as f: pass

            with open("pyproject.toml", "w") as f:
                f.write("""[tool.poetry]\nname = "individual-air-platform"\nversion = "0.1.0"\ndescription = ""\nauthors = ["Your Name <you@example.com>"]\nreadme = "README.md"\npackages = [{\"include\" = \"air\", \"from\" = \"src\"}]\n\n[tool.poetry.dependencies]\npython = "^3.12"\nfastapi = "*"\nuvicorn = {\"extras\" = [\"standard\"], \"version\" = \"*\"}\npydantic = "*"\npydantic-settings = "*"\nhttpx = "*"\nsse-starlette = "*"\n\n\n[tool.poetry.group.dev.dependencies]\npytest = "*"\npytest-asyncio = "*"\npytest-cov = "*"\nblack = "*"\nruff = "*"\nmypy = "*"\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n""")

            tree_output = ["Project directory structure and Poetry initialization conceptually completed."]
            tree_output.append("Placeholder files and directories created:")
            for root, dirs, files in os.walk("."):
                level = root.replace("./", "").count(os.sep)
                indent = ' ' * 4 * (level)
                tree_output.append(f"{indent}{os.path.basename(root)}/")
                for f in files:
                    tree_output.append(f"{indent}    {f}")
            
            return "\n".join(tree_output)
        
        finally:
            os.chdir(original_cwd)
            st.session_state.project_initialized = True

    if not st.session_state.project_initialized:
        if st.button("Simulate Project Initialization"):
            with st.spinner("Creating project structure..."):
                output = simulate_project_init_action()
                st.code(output, language="text")
    else:
        st.success("Project structure conceptually initialized in a temporary location!")
        st.markdown(f"To see the generated structure, you would typically run `ls -R individual-air-platform` in your terminal.")

elif st.session_state.page == "2. Configuration System":
    st.header("2. Robust Configuration with Pydantic v2")
    st.markdown(f"One of the most critical aspects of any production application is its configuration management. Alex, having dealt with numerous bugs due to incorrect environment variables or misconfigured parameters, chooses Pydantic v2 for this task. Pydantic provides robust validation, type checking, and the ability to load settings from various sources (like environment variables or `.env` files). This ensures that the application starts only with valid configurations, preventing runtime errors.")
    st.markdown(f"A key requirement for the \"Predictive Intelligence Engine\" involves dynamic scoring parameters for AI models. For instance, specific weights for model components (e.g., fluency, domain relevance, adaptiveness) must sum to 1.0 to ensure a consistent scoring scale. Alex implements a Pydantic `model_validator` to enforce this business logic.")
    st.markdown(f"The `model_config` `SettingsConfigDict` is used to specify how settings are loaded (e.g., from `.env` files, case insensitivity). Sensitive information, like API keys, is handled with `SecretStr` to prevent accidental logging or exposure.")

    st.markdown(r"The formula for validating component weights is:")
    st.markdown(r"$$ W_{fluency} + W_{domain} + W_{adaptive} = 1.0 $$")
    st.markdown(r"where $W_{fluency}$ is the weight for the fluency component, $W_{domain}$ is the weight for the domain expertise component, and $W_{adaptive}$ is the weight for the adaptiveness component.")
    st.markdown(f"This equation ensures that the individual contributions of different AI model aspects (fluency, domain relevance, adaptability) are correctly normalized and collectively account for the total score, preventing miscalibration of the model's output. If the sum deviates significantly, for example, $abs(W_{sum} - 1.0) > 0.001$, a `ValueError` is raised, indicating an \"invalid configuration\".")

    st.subheader("Implementation (`src/air/config/settings.py`)")
    st.code(
        '''
# Imports (already handled by 'from source import *' and embedded)

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
        ''', 
        language="python"
    )

    st.subheader("Interactive Configuration Validation")
    st.markdown(f"Experiment with the weights for the AI scoring model and observe how Pydantic's `model_validator` enforces the rule that they must sum to 1.0. Also, see how `SecretStr` handles sensitive API keys.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.w_fluency_input = st.number_input(
            "W_FLUENCY",
            min_value=0.0, max_value=1.0, value=st.session_state.w_fluency_input, step=0.01,
            key="input_w_fluency", help="Weight for fluency component (0.0 - 1.0)"
        )
    with col2:
        st.session_state.w_domain_input = st.number_input(
            "W_DOMAIN",
            min_value=0.0, max_value=1.0, value=st.session_state.w_domain_input, step=0.01,
            key="input_w_domain", help="Weight for domain expertise component (0.0 - 1.0)"
        )
    with col3:
        st.session_state.w_adaptive_input = st.number_input(
            "W_ADAPTIVE",
            min_value=0.0, max_value=1.0, value=st.session_state.w_adaptive_input, step=0.01,
            key="input_w_adaptive", help="Weight for adaptiveness component (0.0 - 1.0)"
        )

    st.session_state.openai_api_key_input = st.text_input(
        "OPENAI_API_KEY (simulated secret)",
        value=st.session_state.openai_api_key_input,
        type="password" if not st.session_state.show_raw_api_key else "default",
        key="input_openai_key", help="Enter a simulated API key to see SecretStr in action."
    )

    def validate_and_display_settings():
        get_settings.cache_clear() # Clear cache to ensure new settings are loaded

        # Temporarily set environment variables to simulate loading from .env
        # and allow Pydantic Settings to pick them up
        os.environ['W_FLUENCY'] = str(st.session_state.w_fluency_input)
        os.environ['W_DOMAIN'] = str(st.session_state.w_domain_input)
        os.environ['W_ADAPTIVE'] = str(st.session_state.w_adaptive_input)
        if st.session_state.openai_api_key_input:
            os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key_input
        else:
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']

        output_messages = []
        try:
            current_settings = get_settings() # Reload settings with potentially new env vars
            output_messages.append(f"✅ Configuration Loaded Successfully!")
            output_messages.append(f"**Application Name:** {current_settings.APP_NAME}")
            output_messages.append(f"**Environment:** {current_settings.APP_ENV}")
            output_messages.append(f"**VR Weights:** Fluency={current_settings.W_FLUENCY}, Domain={current_settings.W_DOMAIN}, Adaptive={current_settings.W_ADAPTIVE}")
            output_messages.append(f"**Sum of VR Weights:** {current_settings.W_FLUENCY + current_settings.W_DOMAIN + current_settings.W_ADAPTIVE:.3f}")

            if current_settings.OPENAI_API_KEY:
                output_messages.append(f"**OPENAI_API_KEY (masked by SecretStr):** {current_settings.OPENAI_API_KEY}")
                if st.session_state.show_raw_api_key:
                    output_messages.append(f"**Raw API Key (revealed):** `{current_settings.OPENAI_API_KEY.get_secret_value()}`")
            else:
                output_messages.append(f"**OPENAI_API_KEY:** Not set.")

            st.session_state.current_settings_summary = "\n".join(output_messages)
            st.session_state.config_validation_output = "success"

        except Exception as e: # Catch ValidationErrors and other exceptions
            st.session_state.config_validation_output = f"❌ Configuration Validation Failed: {e}"
            st.session_state.current_settings_summary = ""
        finally:
            # Clean up environment variables
            if 'W_FLUENCY' in os.environ: del os.environ['W_FLUENCY']
            if 'W_DOMAIN' in os.environ: del os.environ['W_DOMAIN']
            if 'W_ADAPTIVE' in os.environ: del os.environ['W_ADAPTIVE']
            if 'OPENAI_API_KEY' in os.environ: del os.environ['OPENAI_API_KEY']
            get_settings.cache_clear() # Clear cache again for subsequent runs
            
    st.button("Validate Configuration", on_click=validate_and_display_settings)

    if st.session_state.config_validation_output:
        if st.session_state.config_validation_output == "success":
            st.success("Configuration validated successfully!")
            st.markdown(st.session_state.current_settings_summary)
            # This checkbox needs to trigger re-validation to update the display of the API key
            new_show_raw_api_key = st.checkbox("Show raw OpenAI API Key value", value=st.session_state.show_raw_api_key, key="show_raw_api_key_checkbox")
            if new_show_raw_api_key != st.session_state.show_raw_api_key:
                st.session_state.show_raw_api_key = new_show_raw_api_key
                validate_and_display_settings() # Re-validate to update raw key display
        else:
            st.error(st.session_state.config_validation_output)

elif st.session_state.page == "3. FastAPI Application Core":
    st.header("3. Building the FastAPI Application Core with Middleware")
    st.markdown(f"Now that the project structure and configuration system are in place, Alex moves on to scaffolding the core FastAPI application. He needs to define the main application entry point (`main.py`) and incorporate essential features for a production-grade API:")
    st.markdown(f"1.  **Application Lifespan Management:** Using FastAPI's `lifespan` context manager ensures that startup tasks (e.g., database connections, caching initialization) and shutdown tasks (e.g., closing connections, resource cleanup) are handled gracefully. This prevents resource leaks and ensures a clean application lifecycle (addressing **Mistake 3: Missing lifespan context manager**).")
    st.markdown(f"2.  **CORS Middleware:** For web applications that might call the API from different domains, Cross-Origin Resource Sharing (CORS) is essential for security and interoperability. `CORSMiddleware` handles the necessary HTTP headers to allow or restrict access.")
    st.markdown(f"3.  **Custom Request Timing Middleware:** To monitor performance and aid in debugging, Alex implements a custom middleware that measures the processing time for each request and adds a unique request ID. This provides valuable observability without cluttering the main business logic.")
    st.markdown(f"These foundational elements are critical for building a reliable and observable API.")

    st.subheader("Implementation (`src/air/api/main.py`)")
    st.code(
        '''
# Imports (already handled by 'from source import *' and embedded)
# health_router, v1_router, v2_router are imported and used below.

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

# The 'app' instance is created globally in source.py during initial import,
# but for interactive demonstration, we simulate its lifecycle aspects.
        ''', 
        language="python"
    )

    def simulate_lifespan_action():
        # Ensure settings are up-to-date for simulation
        current_settings = get_settings() 

        st.session_state.lifespan_log.clear()
        st.session_state.lifespan_log.append(f"🚀 Starting {current_settings.APP_NAME} v{current_settings.APP_VERSION} in {current_settings.APP_ENV} environment...")
        st.session_state.lifespan_log.append("✨ Application startup complete: Database connections, cache initialized.")
        st.session_state.lifespan_log.append("👋 Shutting down application...")
        st.session_state.lifespan_log.append("🛑 Application shutdown complete: Resources released.")
        st.session_state.fastapi_app_configured = True
        # st.rerun() # Not needed here, as the log is displayed immediately after
        # This will trigger an update, but we want to display the log directly without full rerun cycle for immediate feedback.

    st.subheader("Simulate Application Lifecycle")
    st.markdown(f"Click the button below to conceptually simulate the FastAPI application's startup and shutdown sequence, demonstrating the `lifespan` context manager and middleware configuration.")
    if st.button("Simulate App Startup & Shutdown"):
        simulate_lifespan_action()
    
    if st.session_state.fastapi_app_configured:
        st.success("FastAPI application is conceptually configured!")
        st.markdown("**Lifespan Simulation Output:**")
        for log_entry in st.session_state.lifespan_log:
            st.markdown(f"- {log_entry}")
        
        st.markdown(f"**Conceptual API Endpoints:**")
        st.markdown(f"- `/health` (Health Check Endpoint)")
        st.markdown(f"- `{settings.API_V1_PREFIX}/status` (API v1 Status Endpoint)")
        st.markdown(f"- `{settings.API_V2_PREFIX}/status` (API v2 Status Endpoint)")
        st.markdown(f"The `create_app` function embodies the **application factory pattern**, allowing flexible setup. CORS and custom timing middleware are integrated for security and observability.")

elif st.session_state.page == "4. API Versioning":
    st.header("4. API Versioning for Scalability and Evolution")
    st.markdown(f"Alex understands that AI models and service contracts evolve rapidly. To prevent breaking changes for existing users while simultaneously introducing new features or improved models, a clear API versioning strategy is crucial. By defining separate `APIRouter` instances for `v1` and `v2` and associating them with distinct URL prefixes (`/api/v1` and `/api/v2`), he ensures that different versions of the API can coexist. This allows InnovateAI Solutions to deprecate older versions gracefully and onboard new clients to improved interfaces without forcing immediate migrations. This separation is fundamental for maintaining backward compatibility and enabling agile development of new features.")
    
    st.markdown(f"The strategy employs **URI Versioning**, where the API version is embedded directly into the URL path, for example:")
    st.code(f"https://api.innovateai.com/api/v1/predict", language="text")
    st.markdown(r"where `/api/v1` denotes the first version of the API.")
    st.code(f"https://api.innovateai.com/api/v2/predict", language="text")
    st.markdown(r"where `/api/v2` denotes the second, potentially updated, version of the API.")
    st.markdown(f"This approach makes the version explicit and easily understandable by clients.")

    st.subheader("Conceptual Implementation in `main.py`")
    st.code(
        f"""
# ... (within create_app() function) ...

    # --- API Routes ---
    app.include_router(health_router, tags=["Health"])

    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX)

    return app
        """,
        language="python",
        help="This shows how versioned routers are included in the FastAPI app."
    )
    st.markdown(f"This section confirms the logical separation of API versions. By conceptually demonstrating how `v1_router` and `v2_router` would be populated with version-specific endpoints, Alex has laid the groundwork for future API development. New features or breaking changes can be introduced in `v2` without impacting `v1` clients, providing a robust pathway for the PIE platform's growth and evolution. The health check endpoint ensures basic service availability can always be monitored.")

elif st.session_state.page == "5. Production Readiness":
    st.header("5. Conceptualizing Containerization and CI/CD for Production Readiness")
    st.markdown(f"Alex understands that for InnovateAI Solutions to deploy the \"Predictive Intelligence Engine\" reliably, containerization and a robust Continuous Integration/Continuous Deployment (CI/CD) pipeline are essential. These practices ensure that the application runs consistently across different environments and that code changes are automatically tested and validated.")
    st.markdown(f"**Containerization with Docker:** Docker provides isolated, portable environments for the application. This eliminates \"it works on my machine\" problems by packaging the application and all its dependencies into a single, deployable unit (a Docker image). Alex envisions a `Dockerfile` that builds the application image and a `docker-compose.yml` file for defining how the application services (e.g., FastAPI, database, Redis) run together in a local development environment.")
    st.markdown(f"**GitHub Actions Workflow:** For automated testing and quality assurance, Alex will set up a GitHub Actions workflow. This CI pipeline will automatically lint the code, run unit and integration tests, and check code coverage every time changes are pushed to the repository. This proactive approach catches bugs early, maintains code quality, and ensures that only validated code makes it to production.")
    st.markdown(f"While the full implementation of Dockerfiles and GitHub Actions YAMLs are beyond the scope of this initial setup (and are platform-specific deployment steps), Alex has conceptually planned for their integration. Their location and purpose are defined in the project's foundational thinking.")

    st.subheader("Conceptualizing Production Infrastructure")
    st.markdown(f"**Containerization (Docker):**")
    st.markdown(f"Alex plans to create a `Dockerfile` in the project root (`./`) to define the application's runtime environment. This `Dockerfile` will specify the base Python image, install Poetry, add application code, and define the command to run the FastAPI application using Uvicorn.")
    st.markdown(f"For local development and multi-service orchestration, a `docker-compose.yml` file would be used to define how the FastAPI service, along with dependencies like PostgreSQL and Redis, run together in an isolated development environment.")
    st.markdown(f"Example conceptual files:")
    st.code(
        """
  - `Dockerfile` (in project root)
  - `docker-compose.yml` (in project root)
        """,
        language="yaml"
    )

    st.markdown(f"**Continuous Integration (GitHub Actions):**")
    st.markdown(f"Alex will define a GitHub Actions workflow to automate testing and code quality checks. This workflow, typically located in `.github/workflows/ci.yml`, will execute tasks like:")
    st.markdown(f"- Installing Python dependencies with Poetry.")
    st.markdown(f"- Running `black` for consistent code formatting.")
    st.markdown(f"- Running `ruff` for fast code linting.")
    st.markdown(f"- Executing `pytest` for comprehensive unit and integration tests.")
    st.markdown(f"- Checking code coverage with `pytest-cov` to ensure sufficient test coverage.")
    st.markdown(f"Example conceptual file:")
    st.code(
        """
  - `.github/workflows/ci.yml`
        """,
        language="yaml"
    )
    st.markdown(f"These foundational steps, while not fully implemented here, are critical for ensuring the production-readiness, reliability, and maintainability of the AI platform.")

elif st.session_state.page == "6. Troubleshooting":
    st.header("6. Common Mistakes & Troubleshooting")
    st.markdown(f"This section addresses common mistakes encountered when setting up a backend platform and how the design patterns covered in this lab mitigate them.")

    st.subheader("Mistake 1: Weights don't sum to 1.0")
    st.markdown(f"**Problem:** AI model scoring weights (e.g., `W_FLUENCY`, `W_DOMAIN`, `W_ADAPTIVE`) are configured incorrectly and do not sum to 1.0, leading to inaccurate or inconsistent model outputs.")
    st.code(
        """
# WRONG (Example of incorrect configuration)
W_FLUENCY = 0.50
W_DOMAIN = 0.40
W_ADAPTIVE = 0.20 # Sum = 1.10!
        """,
        language="python"
    )
    st.markdown(f"**Fix:** The Pydantic `model_validator` in the `Settings` class catches this at application startup, preventing the application from running with invalid configuration. The interactive configuration section (**2. Configuration System**) demonstrates this directly.")
    st.markdown(f"**Action:** Go back to **2. Configuration System** and try entering `W_FLUENCY=0.50`, `W_DOMAIN=0.40`, and `W_ADAPTIVE=0.25` to see the validation error.")

    st.subheader("Mistake 2: Exposing secrets in logs")
    st.markdown(f"**Problem:** Sensitive information like API keys is accidentally printed to logs or exposed in debugging interfaces, posing a security risk.")
    st.code(
        """
# WRONG (Example of exposing a secret)
print(f"Using key: {settings.OPENAI_API_KEY}")
        """,
        language="python"
    )
    st.markdown(f"**Fix:** Use Pydantic's `SecretStr` type for sensitive fields. `SecretStr` automatically masks the value when printed, requiring an explicit call to `.get_secret_value()` to retrieve the raw string, thus preventing accidental exposure. The interactive configuration section (**2. Configuration System**) demonstrates `SecretStr` behavior.")
    st.markdown(f"**Action:** Go back to **2. Configuration System** and enter a simulated `OPENAI_API_KEY` to observe how it's masked by default.")

    st.subheader("Mistake 3: Missing lifespan context manager")
    st.markdown(f"**Problem:** Application resources (e.g., database connections, cache clients) are not properly initialized or cleaned up during startup and shutdown, leading to resource leaks, connection issues, or unstable behavior.")
    st.code(
        """
# WRONG - No lifespan specified
app = FastAPI() # Resources leak on shutdown
        """, 
        language="python"
    )
    st.markdown(f"**Fix:** Always use FastAPI's `lifespan` context manager to define startup and shutdown logic. This ensures a controlled lifecycle for application resources. The **3. FastAPI Application Core** page demonstrates the correct integration of `lifespan`.")
    st.markdown(f"**Action:** Go back to **3. FastAPI Application Core** and click 'Simulate App Startup & Shutdown' to observe the correct lifespan management.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
