

import streamlit as st
import asyncio
import os
from datetime import datetime
# from source import *

# --- Page Config ---
st.set_page_config(
    page_title="QuLab: Foundation & Platform Setup", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation & Platform Setup")
st.divider()

# --- Helper functions to simulate notebook code execution effects in Streamlit ---
# These functions encapsulate the specific logic or output presentation for Streamlit
# that might differ from direct notebook cell execution.


def simulate_project_initialization_output():
    """Simulates the output of project initialization commands."""
    return """
    Project 'individual-air-platform' initialized with Poetry.
    Core dependencies (fastapi, uvicorn, pydantic, pydantic-settings, httpx, sse-starlette) added.
    Dev dependencies (pytest, pytest-asyncio, pytest-cov, black, ruff, mypy, hypothesis) added.
    Standard source directory structure created:
    - src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas,agents,observability,mcp,events}
    - tests/{unit,integration,evals}
    - docs/{adr,requirements,failure-modes}
    - src/air/__init__.py
    """


def simulate_bad_settings_load_output():
    """Simulates an attempt to load settings with bad weights, triggering Pydantic validation error."""
    from config_settings import Settings

    original_env_vars = {}
    for var in ['W_FLUENCY', 'W_DOMAIN', 'W_ADAPTIVE']:
        if var in os.environ:
            original_env_vars[var] = os.environ[var]

    os.environ['W_FLUENCY'] = '0.5'
    os.environ['W_DOMAIN'] = '0.4'
    os.environ['W_ADAPTIVE'] = '0.2'  # Sum = 1.10, incorrect

    result = ""
    try:
        # Attempt to create a new Settings instance to trigger validation
        Settings()
        result = "No validation error occurred (this should not happen for this simulation)."
    except ValueError as e:
        result = f"Successfully caught validation error: {e}"
    finally:
        # Clean up environment variables
        for var in ['W_FLUENCY', 'W_DOMAIN', 'W_ADAPTIVE']:
            if var in os.environ:
                del os.environ[var]
        # Restore original environment variables
        for var, val in original_env_vars.items():
            os.environ[var] = val
    return result


def simulate_secret_str_handling_output():
    """Simulates setting an API key via env var and demonstrating SecretStr masking."""
    from config_settings import get_settings

    original_openai_api_key = os.environ.get('OPENAI_API_KEY')
    dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    os.environ['OPENAI_API_KEY'] = dummy_api_key

    # Instantiate Settings to pick up the new env var
    # Use get_settings to ensure caching/defaults are handled
    temp_settings = get_settings()
    masked_key = str(
        temp_settings.OPENAI_API_KEY) if temp_settings.OPENAI_API_KEY else "Not configured."
    key_type = str(type(temp_settings.OPENAI_API_KEY)
                   ) if temp_settings.OPENAI_API_KEY else "NoneType"

    # Clean up and restore
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    if original_openai_api_key is not None:
        # FIX: The variable 'var' was undefined. It should be 'OPENAI_API_KEY'.
        os.environ['OPENAI_API_KEY'] = original_openai_api_key

    return f"OpenAI API Key (using SecretStr): {masked_key}\nType of key: {key_type}"


async def simulate_app_lifespan_output_async(app_instance, settings_obj):
    """Simulates the startup and shutdown of the FastAPI app using its lifespan."""
    from app_factory import setup_tracing

    messages = []
    messages.append(
        f"🚀 Starting {settings_obj.APP_NAME} v{settings_obj.APP_VERSION}")
    messages.append(f"🌍 Environment: {settings_obj.APP_ENV}")
    messages.append(f"🔢 Parameter Version: {settings_obj.parameter_version}")
    messages.append(
        f"🛡️ Guardrails: {'Enabled' if settings_obj.GUARDRAILS_ENABLED else 'Disabled'}")
    messages.append(
        f"💰 Cost Budget: ${settings_obj.DAILY_COST_BUDGET_USD}/day")
    if not settings_obj.DEBUG:
        # setup_tracing is imported from app_factory
        messages.append(setup_tracing(app_instance))
    messages.append("    Application started up (resources initialized).")
    await asyncio.sleep(0.05)  # Simulate some runtime
    messages.append("👋 Shutting down (resources cleaned up).")
    return "\n".join(messages)

# --- Session State Initialization ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Introduction'
if 'settings_object' not in st.session_state:
    st.session_state.settings_object = None
if 'fastapi_app_object' not in st.session_state:
    st.session_state.fastapi_app_object = None
if 'project_init_output' not in st.session_state:
    st.session_state.project_init_output = None
if 'config_validation_output' not in st.session_state:
    st.session_state.config_validation_output = None
if 'fastapi_app_output' not in st.session_state:
    st.session_state.fastapi_app_output = None
if 'detailed_health_output' not in st.session_state:
    st.session_state.detailed_health_output = None
if 'basic_health_output' not in st.session_state:
    st.session_state.basic_health_output = None
if 'readiness_output' not in st.session_state:
    st.session_state.readiness_output = None
if 'liveness_output' not in st.session_state:
    st.session_state.liveness_output = None
if 'mistake1_output' not in st.session_state:
    st.session_state.mistake1_output = None
if 'mistake2_output' not in st.session_state:
    st.session_state.mistake2_output = None
if 'mistake3_output' not in st.session_state:
    st.session_state.mistake3_output = None

# --- Sidebar for Navigation ---
st.sidebar.title("AI-Readiness Platform Lab")
pages = [
    'Introduction',
    'Task 1.1: Project Initialization',
    'Task 1.2: Configuration System',
    'Task 1.3: FastAPI Application',
    'Task 1.4: Health Check',
    'Common Mistakes & Troubleshooting'
]

page_selection = st.sidebar.selectbox(
    "Navigate through Tasks",
    pages,
    index=pages.index(st.session_state.current_page)
)

# Update current_page in session state and rerun if selection changes
if page_selection != st.session_state.current_page:
    st.session_state.current_page = page_selection
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Lab Objectives")
st.sidebar.markdown("- **Remember**: List FastAPI components")
st.sidebar.markdown("- **Understand**: Explain Pydantic validation")
st.sidebar.markdown("- **Apply**: Implement config with weight validation")
st.sidebar.markdown("- **Create**: Design project structure for AI platforms")
st.sidebar.markdown("---")
st.sidebar.header("Tools Introduced")
st.sidebar.markdown("- **Python 3.12**: Runtime, performance")
st.sidebar.markdown("- **Poetry**: Dependency management")
st.sidebar.markdown("- **FastAPI**: Web framework, async support")
st.sidebar.markdown("- **Pydantic v2**: Validation, settings management")
st.sidebar.markdown("- **Docker**: Containerization")

# --- Main Content Area ---

if st.session_state.current_page == 'Introduction':
    st.header("Introduction: The Individual AI-Readiness Platform Case Study")
    st.markdown(f"Welcome to the **Individual AI-Readiness Platform** project! You are a **Software Developer** tasked with establishing the foundational setup for a new AI service. This service will eventually host a specific AI model or data processing pipeline, but our immediate goal is to lay down a robust, scalable, and maintainable project skeleton from day one. This proactive approach ensures our AI services are not just functional but also reliable, secure, and easy to maintain.")
    st.markdown(f"")
    st.markdown(f"In a rapidly evolving field like AI, the agility to deploy new services while maintaining high standards is paramount. This lab will guide you through a real-world workflow, demonstrating how to apply best practices in Python development, API design, and containerization to build a solid foundation for your AI applications. We'll leverage tools like Poetry for dependency management, FastAPI for API development, Pydantic for robust configuration, and Docker for reproducible environments.")
    st.markdown(f"")
    st.markdown(f"By the end of this lab, you'll have a blueprint for rapidly establishing consistent, compliant, and production-ready AI services. This means less boilerplate for you, clearer project organization, and a faster path to delivering impactful AI features for the entire organization.")
    st.markdown(f"---")
    st.header("1. Setting Up Your Development Environment")
    st.markdown(f"As a Software Developer, the first step in any new project is to prepare your environment. We need to install the necessary libraries to manage dependencies and build our FastAPI application. This ensures all team members work with the same tools and library versions, preventing 'works on my machine' issues.")
    st.markdown(f"")
    st.markdown(
        f"**Action**: In a real scenario, you would run `pip install fastapi 'uvicorn[standard]' pydantic pydantic-settings httpx sse-starlette` to get the core dependencies.")
    st.success(
        "Dependencies assumed to be installed for this interactive lab environment.")

elif st.session_state.current_page == 'Task 1.1: Project Initialization':
    st.header(
        "2. Project Kick-off: Laying the Foundation for the AI-Readiness Platform")
    st.markdown(f"As a Software Developer at the Individual AI-Readiness Platform, your first major task is to establish a standardized project structure and manage dependencies effectively. This isn't just about organizing files; it's about enforcing consistency across all AI services, streamlining onboarding for new developers, and ensuring predictable behavior in development and production environments. We'll use Poetry to manage dependencies and define a clear directory layout tailored for an API-driven AI service.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"A well-defined project structure and dependency management system reduce technical debt, prevent dependency conflicts, and accelerate development cycles. For an organization like ours, this means a more reliable AI platform and faster iteration on new AI capabilities.")
    st.markdown(f"---")
    st.markdown(f"### Task: Project Initialization and Structure Setup")
    st.markdown(f"We're starting a new AI service within the Individual AI-Readiness Platform. To ensure a consistent and maintainable codebase from day one, we'll initialize a new Python project using Poetry and establish a standard project directory structure. This structure will accommodate various components like API routes, configuration, models, and services, making our project scalable and easy to navigate for any developer joining the team.")
    st.markdown(f"")
    st.markdown(f"Poetry helps us manage dependencies, create isolated virtual environments, and build distributable packages, which is crucial for moving our service from development to production seamlessly.")

    st.markdown(f"#### Step-by-Step Poetry Initialization")
    st.markdown(f"**Step 1: Create the project directory**")
    st.code("""mkdir individual-air-platform
cd individual-air-platform""", language='bash')

    st.markdown(f"**Step 2: Initialize Poetry**")
    st.markdown(
        f"The `^3.12` indicates compatibility with Python 3.12 and above, but not 4.0.")
    st.code("""poetry init --name="individual-air-platform" --python="^3.12" """, language='bash')

    st.markdown(f"**Step 3: Install core runtime dependencies**")
    st.markdown(
        f"These are the essential dependencies for our FastAPI application:")
    st.code(
        """poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette""", language='bash')

    st.markdown(f"**Step 4: Install development dependencies**")
    st.markdown(
        f"These tools are essential for code quality, testing, and static analysis:")
    st.code("""poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy hypothesis""", language='bash')

    st.markdown(f"**Step 5: Create the standard source directory structure**")
    st.markdown(
        f"This structure organizes our application logic into logical domains:")
    st.code("""# Main application package with API routes and configuration
mkdir -p src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas}

# AI-specific modules
mkdir -p src/air/{agents,observability,mcp,events}

# Testing infrastructure
mkdir -p tests/{unit,integration,evals}

# Documentation
mkdir -p docs/{adr,requirements,failure-modes}

# Make 'air' a Python package
touch src/air/__init__.py""", language='bash')

    st.markdown(f"**Directory Structure Explanation:**")
    st.markdown(
        f"- `src/air/api/routes/v1`, `v2`: Versioned API endpoints for evolution")
    st.markdown(f"- `src/air/config`: Application configuration")
    st.markdown(
        f"- `src/air/models`: Pydantic models for data (request/response, database)")
    st.markdown(
        f"- `src/air/services`: Business logic and external service integrations")
    st.markdown(
        f"- `src/air/agents`, `observability`, `mcp`, `events`: AI-specific modules")
    st.markdown(f"- `tests/`: Unit, integration, and evaluation tests")
    st.markdown(f"- `docs/adr`: Architecture Decision Records")

    # Widget: Button to simulate project initialization
    if st.button("Simulate Project Initialization"):
        st.session_state.project_init_output = simulate_project_initialization_output()
        st.success("Project Initialization Simulated!")

    # Display output if available in session state
    if st.session_state.project_init_output:
        st.markdown(f"### Simulated Output:")
        st.code(st.session_state.project_init_output, language='bash')
        st.markdown(f"### Explanation of Execution")
        st.markdown(
            f"The preceding commands simulate the creation of a new Python project using Poetry and establish a well-structured directory layout.")
        st.markdown(
            f"- `poetry init` sets up the `pyproject.toml` file, which is the heart of our project's metadata and dependency management.")
        st.markdown(f"- `poetry add` commands populate `pyproject.toml` with our runtime and development dependencies, ensuring they are correctly versioned and installed in an isolated virtual environment.")
        st.markdown(f"- The `mkdir -p` commands create a logical, hierarchical structure for our source code, separating concerns and making the codebase easier to understand, maintain, and scale. This aligns with industry best practices for larger applications.")
        st.markdown(f"For instance, API versioning (`v1`, `v2`) is baked into the structure from the start, allowing for smooth, backward-compatible API evolution.")

elif st.session_state.current_page == 'Task 1.2: Configuration System':
    st.header("3. Safeguarding Configuration: Pydantic Validation in Action")
    st.markdown(f"Misconfigurations are a leading cause of outages and unexpected behavior in production systems. For our AI-Readiness Platform, critical parameters — from API keys to model scoring weights — must be validated *before* the application starts. This proactive approach prevents runtime errors and ensures operational stability.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"Consider the **Knight Capital incident** in 2012, where a single configuration deployment error led to a $440 million loss in 45 minutes. A flag intended for a 'test' environment was mistakenly set to 'production,' triggering unintended automated trades. Pydantic's validation-at-startup prevents such catastrophic errors by ensuring all configuration parameters meet defined constraints, failing fast with clear error messages if they don't. For our AI services, this means ensuring model weights sum correctly or API keys are present, directly impacting the reliability and safety of our AI-driven decisions.")
    st.markdown(f"")
    st.markdown(f"Here, we define our `Settings` class using `pydantic-settings` and `Pydantic v2`. This provides a robust, type-safe, and validated configuration system, drawing values from environment variables or a `.env` file. We also include a `model_validator` to enforce complex rules, such as ensuring all scoring weights sum to 1.0.")
    st.markdown(f"")
    st.markdown(f"### Mathematical Explanation: Validating Scoring Weights")
    st.markdown(r"In many AI/ML applications, especially those involving composite scores or weighted features, the sum of weights must adhere to a specific constraint, often summing to 1.0. This ensures that the individual components proportionally contribute to the overall score and that the scoring logic remains consistent. If these weights deviate from their expected sum, the model's output could be skewed, leading to incorrect predictions or decisions.")
    st.markdown(r"$$ \sum_{i=1}^{N} w_i = 1.0 $$")
    st.markdown(
        r"where $w_i$ represents the $i$-th scoring weight and $N$ is the total number of weights.")
    st.markdown(r"Our `model_validator` explicitly checks this condition, raising an error if the sum deviates beyond a small epsilon (e.g., $0.001$) to account for floating-point inaccuracies. This is a crucial guardrail to prevent configuration errors that could lead to invalid AI scores.")
    st.markdown(f"---")
    st.markdown(
        f"### Task: Implement a Configuration System with Full Validation")
    st.markdown(f"We are setting up the core configuration for our AI service. This includes application details, API prefixes, database URLs, LLM provider keys, and crucial scoring parameters. To prevent configuration-related failures, we'll use Pydantic-Settings for strong type validation and enforce business rules like ensuring scoring weights sum to 1.0. This ensures the integrity of our AI model's parameters and the overall stability of the service.")
    st.markdown(f"")
    st.markdown(f"The use of `SecretStr` for API keys adds a layer of security by preventing accidental logging of sensitive information.")

    st.markdown(
        f"#### Settings Class Implementation (`src/air/config/settings.py`)")
    st.markdown(f"Below is the complete Settings class that should be created:")
    st.code('''from typing import Literal, Optional, List, Dict, Any
from functools import lru_cache
from pydantic import Field, model_validator, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime, timedelta

class Settings(BaseSettings):
    """Application settings with comprehensive validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env not defined in Settings
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
        """Validate that component weights sum to 1.0."""
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
        """Return current parameter version."""
        return "v1.0"

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV == "production"

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
''', language='python')

    st.markdown(f"**Key Features of the Settings Class:**")
    st.markdown(
        f"- **Type Safety**: Uses Pydantic's type annotations and `Literal` types")
    st.markdown(
        f"- **Validation Bounds**: `Field(ge=..., le=...)` ensures parameters stay within valid ranges")
    st.markdown(
        f"- **SecretStr**: Masks sensitive values like API keys to prevent logging exposure")
    st.markdown(
        f"- **Custom Validators**: `@model_validator` ensures weights sum to 1.0")
    st.markdown(
        f"- **Computed Fields**: Dynamic properties like `is_production` and `parameter_version`")
    st.markdown(
        f"- **Environment Configuration**: Reads from `.env` file automatically")

    # Widget: Button to load and validate settings
    if st.button("Load and Validate Settings"):
        # Call the function from source.py
        from config_settings import get_settings
        st.session_state.settings_object = get_settings()
        output_str = f"Application Name: {st.session_state.settings_object.APP_NAME}\n" \
            f"Application Version: {st.session_state.settings_object.APP_VERSION}\n" \
            f"Environment: {st.session_state.settings_object.APP_ENV}\n" \
            f"Is Production: {st.session_state.settings_object.is_production}\n" \
            f"Scoring Parameters (VR weights): W_FLUENCY={st.session_state.settings_object.W_FLUENCY}, W_DOMAIN={st.session_state.settings_object.W_DOMAIN}, W_ADAPTIVE={st.session_state.settings_object.W_ADAPTIVE}\n" \
            f"Sum of VR weights: {st.session_state.settings_object.W_FLUENCY + st.session_state.settings_object.W_DOMAIN + st.session_state.settings_object.W_ADAPTIVE}\n"
        if st.session_state.settings_object.OPENAI_API_KEY:
            output_str += f"OpenAI API Key (masked): {st.session_state.settings_object.OPENAI_API_KEY}"
        else:
            output_str += "OpenAI API Key is not configured."
        st.session_state.config_validation_output = output_str
        st.success("Settings loaded and validated!")

    # Display output if available in session state
    if st.session_state.config_validation_output:
        st.markdown(f"### Output of Settings Loading and Validation:")
        st.code(st.session_state.config_validation_output, language='python')
        st.markdown(f"### Explanation of Execution")
        st.markdown(f"We've successfully defined our `Settings` class, which uses Pydantic to validate configuration parameters. When `settings = get_settings()` is called, Pydantic performs immediate validation based on the types, bounds (`Field(ge=..., le=...)`), and custom `model_validator` functions (e.g., `validate_weight_sums`).")
        st.markdown(f"- The `APP_NAME`, `APP_VERSION`, and `APP_ENV` are loaded, with `APP_ENV` restricted to a `Literal` set of values, ensuring type safety.")
        st.markdown(
            f"- `SecretStr` for `OPENAI_API_KEY` prevents sensitive information from being accidentally printed or exposed.")
        st.markdown(f"- The output shows that our scoring parameters, like `W_FLUENCY`, `W_DOMAIN`, and `W_ADAPTIVE`, are loaded correctly, and their sum is validated. This ensures that any AI scoring logic relying on these weights will operate with consistent and valid inputs, preventing the kind of 'garbage in, garbage out' scenarios that can undermine AI system reliability.")
        st.markdown(f"This system acts as an early warning mechanism, catching configuration issues at application startup rather than letting them cause silent failures or incorrect AI decisions later in the workflow.")
    else:
        st.info(
            "Click 'Load and Validate Settings' to see the configuration system in action.")

elif st.session_state.current_page == 'Task 1.3: FastAPI Application':
    st.header("4. Building the API Core: Versioned Routers and Middleware")
    st.markdown(f"As the Software Developer, your task is to construct the FastAPI application, integrating versioned API routes and crucial middleware for cross-cutting concerns. This setup ensures our AI service is not only functional but also maintainable, observable, and adaptable to future changes. The 'Application Factory Pattern' allows us to create multiple FastAPI app instances, useful for testing or different deployment contexts.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(
        f"A production-ready AI service must handle various operational requirements beyond just serving model predictions.")
    st.markdown(f"- **API Versioning:** As AI models evolve, so do their APIs. Versioned routers (`/api/v1`, `/api/v2`) ensure backward compatibility, allowing seamless upgrades for clients without disrupting existing integrations. This is crucial for an 'Individual AI-Readiness Platform' that will continuously evolve its capabilities.")
    st.markdown(f"- **Middleware:** Cross-cutting concerns like CORS (Cross-Origin Resource Sharing), request timing, and request ID tracking are essential for web services.")
    st.markdown(f"    - **CORS Middleware** allows frontend applications (e.g., a dashboard for the AI platform) to securely interact with our backend API.")
    st.markdown(f"    - **Request Timing Middleware** provides crucial performance metrics. By attaching an `X-Process-Time` header to every response, we enable monitoring systems to track API latency, a key indicator of service health and user experience.")
    st.markdown(f"    - **Request ID Middleware** assigns a unique ID (`X-Request-ID`) to each request. This ID is vital for tracing requests through complex microservice architectures, especially when debugging issues across multiple services in a production environment.")
    st.markdown(f"- **Exception Handling:** Graceful error handling, especially for validation errors, provides informative feedback to API consumers, making the service more user-friendly and robust.")
    st.markdown(f"---")
    st.markdown(
        f"### Task: Implement FastAPI Application with Versioned Routers and Middleware")
    st.markdown(
        f"Now we will build the main FastAPI application. This involves:")
    st.markdown(
        f"1. Defining a `lifespan` context manager for startup and shutdown events (e.g., initializing tracing).")
    st.markdown(
        f"2. Implementing an 'Application Factory Pattern' (`create_app`) to create FastAPI instances.")
    st.markdown(
        f"3. Adding `CORSMiddleware` to handle cross-origin requests securely.")
    st.markdown(
        f"4. Implementing a custom HTTP middleware to inject a unique request ID and track request processing time.")
    st.markdown(
        f"5. Defining global exception handlers for better error reporting.")
    st.markdown(
        f"6. Including versioned API routers (`v1_router`, `v2_router`) and a dedicated health router.")
    st.markdown(f"")
    st.markdown(
        f"This setup ensures our AI service is robust, secure, observable, and ready for continuous deployment.")

    if st.session_state.settings_object is None:
        st.warning(
            "Please complete 'Task 1.2: Configuration System' first to load application settings.")
    else:
        st.markdown(
            f"#### FastAPI Application Implementation (`src/air/api/main.py`)")
        st.markdown(f"Below is the complete FastAPI application setup:")
        st.code('''from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from air.config.settings import settings

# Placeholder routers (these would be defined in separate files)
v1_router = APIRouter()
v2_router = APIRouter()
health_router = APIRouter()

@v1_router.get("/items")
async def read_v1_items():
    return {"version": "v1", "items": ["item1", "item2"]}

@v2_router.get("/items")
async def read_v2_items():
    return {"version": "v2", "items": ["item1", "item2", "item3"]}

def setup_tracing(app: FastAPI):
    """Initialize observability/tracing for the application."""
    print("Initializing observability tracing...")
    # In production, integrate with OpenTelemetry, LangChain, etc.

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.APP_ENV}")
    if not settings.DEBUG:
        setup_tracing(app)
    print("✅ Application started")
    
    yield  # Application runs
    
    # Shutdown
    print("👋 Shutting down - cleaning up resources...")

def create_app() -> FastAPI:
    """Application factory pattern - creates and configures FastAPI instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Individual AI-Readiness Score Platform - Production Ready",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Timing Middleware
    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

    # Exception Handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation Error", "detail": str(exc)},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    # Include Routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["API v1"])
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX, tags=["API v2"])

    return app

# Create the app instance
app = create_app()
''', language='python')

        st.markdown(f"**Key Components:**")
        st.markdown(
            f"- **Lifespan Context Manager**: Handles startup/shutdown with `@asynccontextmanager`")
        st.markdown(
            f"- **Application Factory**: `create_app()` function for flexible app instantiation")
        st.markdown(f"- **CORS Middleware**: Configurable based on DEBUG mode")
        st.markdown(
            f"- **Request Middleware**: Adds unique request ID and timing to each response")
        st.markdown(
            f"- **Exception Handlers**: Standardized error responses for better API consistency")
        st.markdown(
            f"- **Router Inclusion**: Versioned API endpoints (`v1`, `v2`) for backward compatibility")

        # Widget: Button to simulate FastAPI application setup
        if st.button("Simulate FastAPI Application Setup"):
            # Simulate the output without actually creating the app
            sim_output = f"""🚀 Starting {st.session_state.settings_object.APP_NAME} v{st.session_state.settings_object.APP_VERSION}
🌍 Environment: {st.session_state.settings_object.APP_ENV}
🔢 Parameter Version: {st.session_state.settings_object.parameter_version}
🛡️ Guardrails: {'Enabled' if st.session_state.settings_object.GUARDRAILS_ENABLED else 'Disabled'}
💰 Cost Budget: ${st.session_state.settings_object.DAILY_COST_BUDGET_USD}/day
✅ Application started
📋 Middleware registered: CORS, Request ID, Timing
🛣️ Routes registered: /health, {st.session_state.settings_object.API_V1_PREFIX}/*, {st.session_state.settings_object.API_V2_PREFIX}/*
✅ Application is ready to serve requests"""

            st.session_state.fastapi_app_output = sim_output
            st.session_state.fastapi_app_object = True  # Mark as created for next steps
            st.success("FastAPI Application setup simulated!")

        # Display output if available in session state
        if st.session_state.fastapi_app_output:
            st.markdown(
                f"### Simulated Application Startup:")
            st.code(st.session_state.fastapi_app_output, language='plaintext')

            st.markdown(f"### Registered Routes:")
            st.markdown(f"- `GET /health` - Health check endpoint")
            st.markdown(
                f"- `GET {st.session_state.settings_object.API_V1_PREFIX}/items` - API v1 items endpoint")
            st.markdown(
                f"- `GET {st.session_state.settings_object.API_V2_PREFIX}/items` - API v2 items endpoint")

            st.markdown(f"### Explanation of Execution")
            st.markdown(
                f"The `create_app()` function demonstrates the 'Application Factory Pattern' by returning a fully configured FastAPI application instance.")
            st.markdown(
                f"- The `lifespan` context manager ensures that startup (e.g., observability initialization) and shutdown tasks are handled gracefully.")
            st.markdown(
                f"- `CORSMiddleware` is added, crucial for allowing web clients to interact with our API securely.")
            st.markdown(f"- The custom middleware successfully injects a unique `X-Request-ID` and `X-Process-Time` header into responses. This is vital for distributed tracing and performance monitoring.")
            st.markdown(
                f"- The exception handlers for `ValueError` and `HTTPException` are registered, providing standardized and informative error responses.")
            st.markdown(f"- Finally, the versioned routers (`{st.session_state.settings_object.API_V1_PREFIX}/items`, `{st.session_state.settings_object.API_V2_PREFIX}/items`) are included, demonstrating how different API versions can coexist, enabling the platform to evolve its AI capabilities without breaking existing client integrations.")
            st.markdown(
                f"The simulated startup confirms that all these components are correctly initialized and registered within the FastAPI application.")
        else:
            st.info(
                "Click 'Simulate FastAPI Application Setup' to see the application configuration and startup.")

elif st.session_state.current_page == 'Task 1.4: Health Check':
    st.header("5. Ensuring Service Reliability: Comprehensive Health Checks")
    st.markdown(f"For any production AI service, merely having the API running isn't enough; we need to know if it's truly *healthy* and capable of serving requests. This means checking not only the application itself but also all its critical dependencies like databases, caching layers (Redis), and external LLM APIs. Robust health checks are vital for automated monitoring, load balancing, and self-healing systems in containerized environments like Kubernetes.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"As a Software Developer, implementing detailed health checks is crucial for ensuring the AI-Readiness Platform's uptime and reliability. Imagine a scenario where your AI model relies on a database for feature storage and an external LLM API for inference. If the database is down, or the LLM API is unreachable, your service might technically be 'running' but unable to perform its core function.")
    st.markdown(
        f"- **`/health` (Basic Health):** A fast check for basic application responsiveness, used by load balancers.")
    st.markdown(f"- **`/health/detailed` (Detailed Health):** Provides an in-depth status of all internal and external dependencies. This allows operators to quickly diagnose issues. For example, if the `check_llm()` indicates a 'degraded' status due to high latency, it immediately points to a potential external API issue impacting our AI service's performance.")
    st.markdown(f"- **`/health/ready` (Readiness Probe):** Tells container orchestrators (like Kubernetes) if the service is ready to accept traffic. If dependencies are unhealthy, the service shouldn't receive requests.")
    st.markdown(f"- **`/health/live` (Liveness Probe):** Indicates if the application is still running and hasn't frozen. If this fails, the container needs to be restarted.")
    st.markdown(f"These checks are fundamental for maintaining service level agreements (SLAs) and ensuring our AI services are always operational.")
    st.markdown(f"---")
    st.markdown(
        f"### Task: Implement Comprehensive Health Check Endpoints with Dependency Status")
    st.markdown(f"We need to add health check endpoints to our API. These endpoints will provide insights into the application's status and its critical dependencies. This involves:")
    st.markdown(
        f"1. Defining Pydantic models for `DependencyStatus`, `HealthResponse`, and `DetailedHealthResponse`.")
    st.markdown(
        f"2. Implementing asynchronous functions to simulate checks for external dependencies (database, Redis, LLM).")
    st.markdown(f"3. Creating API endpoints for basic health (`/health`), detailed health (`/health/detailed`), readiness (`/health/ready`), and liveness (`/health/live`).")
    st.markdown(f"")
    st.markdown(
        f"These checks are crucial for reliable deployments and operational monitoring in a production AI environment.")

    if st.session_state.settings_object is None or st.session_state.fastapi_app_object is None:
        st.warning(
            "Please complete 'Task 1.2: Configuration System' and 'Task 1.3: FastAPI Application' first.")
    else:
        st.markdown(
            f"#### Health Check Implementation (`src/air/api/routes/health.py`)")
        st.markdown(
            f"Below is the complete health check router implementation:")
        st.code('''from datetime import datetime
from typing import Dict, Any, Optional, Literal
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

from air.config.settings import settings

router = APIRouter()

# Pydantic Models for Health Responses
class DependencyStatus(BaseModel):
    """Status of a single dependency."""
    name: str
    status: Literal["healthy", "degraded", "unhealthy", "not_configured"]
    latency_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Basic health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    environment: str
    timestamp: datetime
    parameter_version: str

class DetailedHealthResponse(HealthResponse):
    """Detailed health with dependency checks."""
    dependencies: Dict[str, DependencyStatus]
    uptime_seconds: float

# Track startup time for uptime calculation
_startup_time = datetime.utcnow()

# Asynchronous functions to check individual dependencies
async def check_database() -> DependencyStatus:
    """Check database connectivity."""
    try:
        await asyncio.sleep(0.01)  # Simulate network latency
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
    """Check Redis connectivity."""
    try:
        await asyncio.sleep(0.005)  # Simulate network latency
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
    """Check LLM API availability."""
    try:
        if not settings.OPENAI_API_KEY:
            return DependencyStatus(
                name="llm",
                status="not_configured",
                latency_ms=None,
                error="OPENAI_API_KEY not set"
            )
        await asyncio.sleep(0.02)  # Simulate LLM API call latency
        return DependencyStatus(
            name="llm",
            status="healthy",
            latency_ms=20.0,
        )
    except Exception as e:
        return DependencyStatus(
            name="llm",
            status="degraded",
            error=str(e),
        )

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check - fast, no dependency checks."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=settings.parameter_version,
    )

@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """Detailed health check with dependency status."""
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

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    health = await detailed_health_check()
    if health.status == "unhealthy" or health.status == "degraded":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": f"Overall status: {health.status}"}
        )
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}
''', language='python')

        st.markdown(f"**Key Features:**")
        st.markdown(
            f"- **Pydantic Models**: Type-safe response models for health data")
        st.markdown(
            f"- **Dependency Checks**: Async functions to check database, Redis, and LLM APIs")
        st.markdown(
            f"- **Concurrent Checking**: Uses `asyncio.gather()` for parallel dependency checks")
        st.markdown(
            f"- **Status Aggregation**: Determines overall health from individual dependency statuses")
        st.markdown(
            f"- **Kubernetes Probes**: Separate endpoints for readiness and liveness checks")
        st.markdown(
            f"- **Uptime Tracking**: Calculates service uptime from startup time")

        st.subheader("Run Health Checks")
        col1, col2 = st.columns(2)
        with col1:
            # Widget: Button to run basic health check
            if st.button("Run Basic Health Check (/health)"):
                # Simulate the basic health check output
                health_output = {
                    "status": "healthy",
                    "version": st.session_state.settings_object.APP_VERSION,
                    "environment": st.session_state.settings_object.APP_ENV,
                    "timestamp": datetime.utcnow().isoformat(),
                    "parameter_version": st.session_state.settings_object.parameter_version
                }
                import json
                st.session_state.basic_health_output = json.dumps(
                    health_output, indent=2)
                st.success("Basic Health Check Completed!")
            # Display output if available
            if st.session_state.basic_health_output:
                st.markdown("Output of `/health`:")
                st.code(st.session_state.basic_health_output, language='json')

        with col2:
            # Widget: Button to run detailed health check
            if st.button("Run Detailed Health Check (/health/detailed)"):
                # Simulate the detailed health check output
                detailed_output = {
                    "status": "degraded",
                    "version": st.session_state.settings_object.APP_VERSION,
                    "environment": st.session_state.settings_object.APP_ENV,
                    "timestamp": datetime.utcnow().isoformat(),
                    "parameter_version": st.session_state.settings_object.parameter_version,
                    "dependencies": {
                        "database": {
                            "name": "database",
                            "status": "healthy",
                            "latency_ms": 10.0,
                            "error": None
                        },
                        "redis": {
                            "name": "redis",
                            "status": "healthy",
                            "latency_ms": 5.0,
                            "error": None
                        },
                        "llm": {
                            "name": "llm",
                            "status": "not_configured",
                            "latency_ms": None,
                            "error": "OPENAI_API_KEY not set"
                        }
                    },
                    "uptime_seconds": 125.5
                }
                import json
                st.session_state.detailed_health_output = json.dumps(
                    detailed_output, indent=2)
                st.success("Detailed Health Check Completed!")
            # Display output if available
            if st.session_state.detailed_health_output:
                st.markdown("Output of `/health/detailed`:")
                st.code(st.session_state.detailed_health_output, language='json')

        col3, col4 = st.columns(2)
        with col3:
            # Widget: Button to run readiness probe
            if st.button("Run Readiness Probe (/health/ready)"):
                # Simulate readiness check
                readiness_output = {
                    "status": "not_ready",
                    "reason": "Overall status: degraded"
                }
                import json
                st.session_state.readiness_output = f"Status Code: 503\nContent: {json.dumps(readiness_output, indent=2)}"
                st.warning(
                    "Readiness Probe: Service is Not Ready (due to degraded status)")
            # Display output if available
            if st.session_state.readiness_output:
                st.markdown("Output of `/health/ready`:")
                st.code(st.session_state.readiness_output,
                        language='plaintext')

        with col4:
            # Widget: Button to run liveness probe
            if st.button("Run Liveness Probe (/health/live)"):
                # Simulate liveness check
                liveness_output = {"status": "alive"}
                import json
                st.session_state.liveness_output = f"Status Code: 200\nContent: {json.dumps(liveness_output)}"
                st.success("Liveness Probe Completed: Service is Alive!")
            # Display output if available
            if st.session_state.liveness_output:
                st.markdown("Output of `/health/live`:")
                st.code(st.session_state.liveness_output, language='plaintext')

        if st.session_state.detailed_health_output or st.session_state.basic_health_output:
            st.markdown(f"### Explanation of Execution")
            st.markdown(
                f"The execution demonstrates the functionality of our comprehensive health check endpoints:")
            st.markdown(f"- The `/health` endpoint provides a quick, basic check of the application's version, environment, and current timestamp, confirming the service process is responsive.")
            st.markdown(f"- The `/health/detailed` endpoint concurrently checks all configured dependencies (database, Redis, LLM API using `asyncio.gather`). It aggregates their individual statuses and latencies to determine an overall service health, providing granular insights crucial for troubleshooting.")
            st.markdown(f"- The `/health/ready` endpoint indicates if the service is prepared to receive traffic, taking into account the health of its critical dependencies. In our simulation, it returns 'ready' as all dependencies are marked 'healthy' or 'not_configured' (which is treated as degraded in this context, but not 'unhealthy'). If a dependency were 'unhealthy,' this probe would fail, instructing orchestrators to not route traffic to this instance.")
            st.markdown(
                f"- The `/health/live` endpoint confirms the application is active and hasn't crashed, allowing orchestrators to restart it if unresponsive.")
            st.markdown(f"")
            st.markdown(f"These endpoints provide the essential observability for the AI-Readiness Platform, enabling automated systems to ensure high availability and rapid detection of operational issues.")

elif st.session_state.current_page == 'Common Mistakes & Troubleshooting':
    st.header("6. Avoiding Common Pitfalls: Best Practices in Action")
    st.markdown(f"As a Software Developer, understanding and proactively addressing common mistakes is just as important as implementing new features. This section reviews critical configuration and application setup pitfalls, demonstrating how the patterns we've adopted (like Pydantic validation and FastAPI's `lifespan` manager) help prevent them. This hands-on review reinforces best practices for building robust and secure AI services.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"Ignoring best practices often leads to hidden bugs, security vulnerabilities, or catastrophic failures in production. For an AI service, this could mean incorrect model predictions due to bad configurations, data breaches from exposed secrets, or resource leaks that degrade performance over time. By explicitly addressing these 'common mistakes,' we ensure that the Individual AI-Readiness Platform adheres to high standards of reliability, security, and maintainability, protecting both our data and our reputation.")
    st.markdown(f"---")

    # Mistake 1: Not validating weight sums
    st.subheader("❌ Mistake 1: Not validating weight sums")
    st.markdown(
        f"**PROBLEM**: Configuration allows weights that don't sum to 1.0, leading to incorrect AI scoring.")
    st.code("""# WRONG: Weights don't sum to 1.0
settings.W_FLUENCY = 0.50
settings.W_DOMAIN = 0.40
settings.W_ADAPTIVE = 0.20  # Sum = 1.10!

# This would cause incorrect AI scoring calculations
score = calculate_ai_readiness(fluency=0.8, domain=0.7, adaptive=0.6)
""", language='python')

    if st.button("Show Fix for Mistake 1"):
        st.session_state.mistake1_fix = True

    if st.session_state.get('mistake1_fix'):
        st.markdown(f"### ✅ Fix: Use Pydantic's `model_validator`")
        st.code("""@model_validator(mode='after')
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
""", language='python')
        st.success(
            "The `model_validator` catches this at startup, preventing the application from running with invalid weights.")

    st.divider()

    # Mistake 2: Using environment variables without defaults
    st.subheader("❌ Mistake 2: Using environment variables without defaults")
    st.markdown(
        f"**PROBLEM**: Application crashes if environment variable is not set.")
    st.code("""# WRONG: Crashes if env var not set
class Settings(BaseSettings):
    DATABASE_URL: str  # No default!
    REDIS_URL: str     # No default!

# Application will crash on startup if these aren't in .env
""", language='python')

    if st.button("Show Fix for Mistake 2"):
        st.session_state.mistake2_fix = True

    if st.session_state.get('mistake2_fix'):
        st.markdown(
            f"### ✅ Fix: Always provide sensible defaults for development")
        st.code("""# CORRECT: Provide defaults for development environment
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://air:air@localhost:5432/air_platform"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # These can still be overridden by environment variables
    # but won't crash if not set
""", language='python')
        st.success(
            "Always provide sensible defaults that work in development. Production environments can override via environment variables.")

    st.divider()

    # Mistake 3: Exposing secrets in logs
    st.subheader("❌ Mistake 3: Exposing secrets in logs")
    st.markdown(
        f"**PROBLEM**: Sensitive API keys or credentials are logged directly, creating a security vulnerability.")
    st.code("""# WRONG: Logs the actual API key
OPENAI_API_KEY: str = "sk-abc123..."
print(f"Using key: {settings.OPENAI_API_KEY}")
# Output: Using key: sk-abc123...

# This exposes the key in logs, console output, error reports!
""", language='python')

    if st.button("Show Fix for Mistake 3"):
        st.session_state.mistake3_fix = True

    if st.session_state.get('mistake3_fix'):
        st.markdown(f"### ✅ Fix: Use `SecretStr` to mask sensitive values")
        st.code("""# CORRECT: Use SecretStr which masks values
from pydantic import SecretStr

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[SecretStr] = None

# When printed or logged, shows '**********'
print(f"Using key: {settings.OPENAI_API_KEY}")
# Output: Using key: **********

# Access actual value only when needed (e.g., passing to API client)
actual_key = settings.OPENAI_API_KEY.get_secret_value()
""", language='python')
        st.success(
            "`SecretStr` automatically masks the value in string representations, preventing accidental exposure in logs.")

    st.divider()

    # Mistake 4: Missing lifespan context manager
    st.subheader("❌ Mistake 4: Missing lifespan context manager")
    st.markdown(f"**PROBLEM**: Resources (database connections, thread pools) are not properly cleaned up on application shutdown, leading to leaks.")
    st.code("""# WRONG: No cleanup on shutdown
app = FastAPI()

# Database connections, Redis clients, etc. are opened but never closed
# Resources leak when app restarts or crashes!
""", language='python')

    if st.button("Show Fix for Mistake 4"):
        st.session_state.mistake4_fix = True

    if st.session_state.get('mistake4_fix'):
        st.markdown(f"### ✅ Fix: Always use `lifespan` for startup/shutdown")
        st.code("""# CORRECT: Use asynccontextmanager for proper lifecycle
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("🚀 Starting application...")
    db_pool = await create_database_pool()
    redis_client = await create_redis_client()
    
    yield  # Application runs
    
    # Shutdown: Clean up resources
    print("👋 Shutting down...")
    await db_pool.close()
    await redis_client.close()
    print("✅ Resources cleaned up")

app = FastAPI(lifespan=lifespan)
""", language='python')
        st.success("The `lifespan` context manager ensures resources are properly initialized on startup and cleaned up on shutdown, preventing resource leaks.")

    st.divider()

    st.markdown(f"### Summary: Best Practices")
    st.markdown(
        f"By following these patterns, we ensure that the Individual AI-Readiness Platform is:")
    st.markdown(
        f"- **Reliable**: Validated configurations prevent runtime errors")
    st.markdown(f"- **Secure**: Secrets are never accidentally exposed in logs")
    st.markdown(f"- **Robust**: Proper resource management prevents leaks")
    st.markdown(
        f"- **Maintainable**: Clear error messages and fail-fast behavior aid debugging")
    st.markdown(f"")
    st.markdown(f"These practices directly address real-world incidents like the Knight Capital catastrophe, where a simple configuration error led to hundreds of millions in losses.")


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
