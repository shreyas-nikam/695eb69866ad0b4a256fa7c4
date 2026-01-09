
import streamlit as st
import asyncio
from datetime import datetime, timedelta
from typing import Literal, Optional, List, Dict, Any
import os
import sys
import uuid
import time
from functools import lru_cache
from pydantic import Field, model_validator, SecretStr, BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

# --- Page Configuration ---
st.set_page_config(page_title="QuLab: Foundation & Platform Setup", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation & Platform Setup")
st.divider()

# --- Replicating Definitions from source.py for Streamlit's context ---

# Mock create_file to just log the action in Streamlit
def create_file(path, content=""):
    st.info(f"Simulating file creation: `{path}`")

# Mock setup_tracing as it's a placeholder in source.py
def setup_tracing(app: Any):
    st.info("Simulating: Initializing observability tracing...")

# Pydantic Settings class from source.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore", # Ignore extra fields in .env not defined in Settings
    )
    APP_NAME: str = "Individual AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://air:air@localhost:5432/air_platform"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    MODEL_ASSESSMENT: str = "claude-sonnet-4-20250514"
    MODEL_SCORING: str = "gpt-4-turbo"
    MODEL_CHAT: str = "claude-haiku-4-5-20251001"
    MODEL_EMBEDDING: str = "text-embedding-3-small"
    MODEL_FALLBACK_CHAIN: List[str] = [ "gpt-4-turbo", "claude-sonnet-4-20250514", "gpt-3.5-turbo", ]
    DAILY_COST_BUDGET_USD: float = Field(default=100.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1.0)
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
    ONET_API_URL: str = "https://services.onetcenter.org/ws/"
    ONET_API_KEY: Optional[SecretStr] = None
    BLS_API_URL: str = "https://api.bls.gov/publicAPI/v2/"
    BLS_API_KEY: Optional[SecretStr] = None
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    LANGSMITH_API_KEY: Optional[SecretStr] = None
    LANGSMITH_PROJECT: str = "individual-air-platform"
    GUARDRAILS_ENABLED: bool = True
    PII_DETECTION_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    BATCH_MAX_CONCURRENCY: int = 10

    @model_validator(mode='after')
    def validate_weight_sums(self) -> 'Settings':
        vr_sum = self.W_FLUENCY + self.W_DOMAIN + self.W_ADAPTIVE
        if abs(vr_sum - 1.0) > 0.001:
            raise ValueError(f"V^R weights must sum to 1.0, got {vr_sum}")
        fluency_sum = (self.THETA_TECHNICAL + self.THETA_PRODUCTIVITY +
                       self.THETA_JUDGMENT + self.THETA_VELOCITY)
        if abs(fluency_sum - 1.0) > 0.001:
            raise ValueError(f"Fluency weights must sum to 1.0, got {fluency_sum}")
        return self

    @computed_field
    @property
    def parameter_version(self) -> str:
        return "v1.0"

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

@lru_cache
def get_settings() -> Settings:
    return Settings()

# Pydantic Health Check Models from source.py
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

# Modified dependency check functions to respect Streamlit session state
async def check_database_notebook_st(simulated_status: str) -> DependencyStatus:
    await asyncio.sleep(0.01) # Simulate network latency
    if simulated_status == "healthy":
        return DependencyStatus(name="database", status="healthy", latency_ms=10.0)
    elif simulated_status == "degraded":
        return DependencyStatus(name="database", status="degraded", error="Simulated degraded database response")
    else: # unhealthy
        return DependencyStatus(name="database", status="unhealthy", error="Simulated database connection error")

async def check_redis_notebook_st(simulated_status: str) -> DependencyStatus:
    await asyncio.sleep(0.005) # Simulate network latency
    if simulated_status == "healthy":
        return DependencyStatus(name="redis", status="healthy", latency_ms=5.0)
    elif simulated_status == "degraded":
        return DependencyStatus(name="redis", status="degraded", error="Simulated degraded Redis response")
    else: # unhealthy
        return DependencyStatus(name="redis", status="unhealthy", error="Simulated Redis connection error")

async def check_llm_notebook_st(simulated_status: str, api_key: Optional[str]) -> DependencyStatus:
    if not api_key:
        return DependencyStatus(name="llm", status="not_configured", error="OPENAI_API_KEY not set")
    await asyncio.sleep(0.02) # Simulate LLM API call latency
    if simulated_status == "healthy":
        return DependencyStatus(name="llm", status="healthy", latency_ms=20.0)
    elif simulated_status == "degraded":
        return DependencyStatus(name="llm", status="degraded", error="Simulated degraded LLM API response")
    else: # unhealthy
        return DependencyStatus(name="llm", status="unhealthy", error="Simulated LLM API connection error")

# Health check endpoint logic (from source.py, adapted for Streamlit)
async def health_check_func_st(current_settings: Settings) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=current_settings.APP_VERSION,
        environment=current_settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=current_settings.parameter_version,
    )

async def detailed_health_check_func_st(current_settings: Settings, simulated_db: str, simulated_redis: str, simulated_llm: str, openai_key: Optional[str]) -> DetailedHealthResponse:
    db_status, redis_status, llm_status = await asyncio.gather(
        check_database_notebook_st(simulated_db),
        check_redis_notebook_st(simulated_redis),
        check_llm_notebook_st(simulated_llm, openai_key),
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
            # Consider not_configured as degraded if no other issues
            overall_status = "degraded" 

    uptime = (datetime.utcnow() - st.session_state.simulated_startup_time).total_seconds()
    return DetailedHealthResponse(
        status=overall_status,
        version=current_settings.APP_VERSION,
        environment=current_settings.APP_ENV,
        timestamp=datetime.utcnow(),
        parameter_version=current_settings.parameter_version,
        dependencies=dependencies,
        uptime_seconds=uptime,
    )

async def readiness_check_func_st(current_settings: Settings, simulated_db: str, simulated_redis: str, simulated_llm: str, openai_key: Optional[str]):
    health = await detailed_health_check_func_st(current_settings, simulated_db, simulated_redis, simulated_llm, openai_key)
    if health.status == "unhealthy" or health.status == "degraded":
        return {"status": "not_ready", "reason": f"Overall status: {health.status}"}, 503 # HTTP 503 Service Unavailable
    return {"status": "ready"}, 200 # HTTP 200 OK

async def liveness_check_func_st():
    return {"status": "alive"}, 200 # HTTP 200 OK

# --- Initialize Session State ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Introduction"
if "project_initialized" not in st.session_state:
    st.session_state.project_initialized = False
if "settings_configured" not in st.session_state:
    st.session_state.settings_configured = False
if "current_settings" not in st.session_state:
    st.session_state.current_settings = get_settings()
if "api_core_built" not in st.session_state:
    st.session_state.api_core_built = False
if "health_checks_implemented" not in st.session_state:
    st.session_state.health_checks_implemented = False
if "simulated_db_status" not in st.session_state:
    st.session_state.simulated_db_status = "healthy"
if "simulated_redis_status" not in st.session_state:
    st.session_state.simulated_redis_status = "healthy"
if "simulated_llm_status" not in st.session_state:
    st.session_state.simulated_llm_status = "healthy"
if "openai_api_key_configured" not in st.session_state:
    st.session_state.openai_api_key_configured = ""
if "simulated_startup_time" not in st.session_state:
    st.session_state.simulated_startup_time = datetime.utcnow()
if "last_health_response" not in st.session_state:
    st.session_state.last_health_response = None

# Initialize simulation weights from current_settings if they are not already in session_state
if "sim_w_fluency" not in st.session_state:
    st.session_state.sim_w_fluency = st.session_state.current_settings.W_FLUENCY
if "sim_w_domain" not in st.session_state:
    st.session_state.sim_w_domain = st.session_state.current_settings.W_DOMAIN
if "sim_w_adaptive" not in st.session_state:
    st.session_state.sim_w_adaptive = st.session_state.current_settings.W_ADAPTIVE
if "sim_theta_technical" not in st.session_state:
    st.session_state.sim_theta_technical = st.session_state.current_settings.THETA_TECHNICAL
if "sim_theta_productivity" not in st.session_state:
    st.session_state.sim_theta_productivity = st.session_state.current_settings.THETA_PRODUCTIVITY
if "sim_theta_judgment" not in st.session_state:
    st.session_state.sim_theta_judgment = st.session_state.current_settings.THETA_JUDGMENT
if "sim_theta_velocity" not in st.session_state:
    st.session_state.sim_theta_velocity = st.session_state.current_settings.THETA_VELOCITY

# --- Sidebar Navigation ---
page_options = [
    "Introduction",
    "1. Project Initialization",
    "2. Configuration System",
    "3. API Core & Middleware",
    "4. Health Checks",
    "5. Common Pitfalls & Best Practices"
]
st.session_state.current_page = st.sidebar.selectbox(
    "Navigate Lab Sections",
    page_options,
    index=page_options.index(st.session_state.current_page)
)

# --- Page Content: Conditional Rendering ---

# Page: Introduction
if st.session_state.current_page == "Introduction":
    st.title("Introduction: The Individual AI-Readiness Platform Case Study")
    st.markdown(f"Welcome to the **Individual AI-Readiness Platform** project! You are a **Software Developer** tasked with establishing the foundational setup for a new AI service. This service will eventually host a specific AI model or data processing pipeline, but our immediate goal is to lay down a robust, scalable, and maintainable project skeleton from day one. This proactive approach ensures our AI services are not just functional but also reliable, secure, and easy to maintain.")
    st.markdown(f"In a rapidly evolving field like AI, the agility to deploy new services while maintaining high standards is paramount. This lab will guide you through a real-world workflow, demonstrating how to apply best practices in Python development, API design, and containerization to build a solid foundation for your AI applications. We'll leverage tools like Poetry for dependency management, FastAPI for API development, Pydantic for robust configuration, and Docker for reproducible environments.")
    st.markdown(f"By the end of this lab, you'll have a blueprint for rapidly establishing consistent, compliant, and production-ready AI services. This means less boilerplate for you, clearer project organization, and a faster path to delivering impactful AI features for the entire organization.")

    st.subheader("Lab Objectives")
    st.markdown(f"- **Remember**: List the components of a FastAPI application")
    st.markdown(f"- **Understand**: Explain why Pydantic validation prevents configuration errors")
    st.markdown(f"- **Apply**: Implement a configuration system with weight validation")
    st.markdown(f"- **Create**: Design a project structure for production AI platforms")

    st.subheader("Tools Introduced")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"**Tool**")
    with col2: st.markdown(f"**Purpose**")
    with col3: st.markdown(f"**Why This Tool**")
    st.divider()
    with col1: st.markdown(f"Python 3.12")
    with col2: st.markdown(f"Runtime")
    with col3: st.markdown(f"Pattern matching, performance improvements")
    with col1: st.markdown(f"Poetry")
    with col2: st.markdown(f"Dependency management")
    with col3: st.markdown(f"Lock files, virtual environments")
    with col1: st.markdown(f"FastAPI")
    with col2: st.markdown(f"Web framework")
    with col3: st.markdown(f"Async support, automatic OpenAPI")
    with col1: st.markdown(f"Pydantic v2")
    with col2: st.markdown(f"Validation")
    with col3: st.markdown(f"Type safety, settings management")
    with col1: st.markdown(f"Docker")
    with col2: st.markdown(f"Containerization")
    with col3: st.markdown(f"Reproducible environments")
    with col1: st.markdown(f"Docker Compose")
    with col2: st.markdown(f"Multi-container")
    with col3: st.markdown(f"Local development")

# Page: Project Initialization
elif st.session_state.current_page == "1. Project Initialization":
    st.title("1. Setting Up Your Development Environment")
    st.markdown(f"As a Software Developer, the first step in any new project is to prepare your environment. We need to install the necessary libraries to manage dependencies and build our FastAPI application. This ensures all team members work with the same tools and library versions, preventing \"works on my machine\" issues.")

    st.subheader("Project Kick-off: Laying the Foundation for the AI-Readiness Platform")
    st.markdown(f"As a Software Developer at the Individual AI-Readiness Platform, your first major task is to establish a standardized project structure and manage dependencies effectively. This isn't just about organizing files; it's about enforcing consistency across all AI services, streamlining onboarding for new developers, and ensuring predictable behavior in development and production environments. We'll use Poetry to manage dependencies and define a clear directory layout tailored for an API-driven AI service.")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"A well-defined project structure and dependency management system reduce technical debt, prevent dependency conflicts, and accelerate development cycles. For an organization like ours, this means a more reliable AI platform and faster iteration on new AI capabilities.")

    st.markdown(f"---")
    st.subheader("Action: Initialize Project Structure")
    st.markdown(f"Click the button below to simulate the creation of the project directory and `pyproject.toml` file, and the installation of core and dev dependencies.")
    
    # Widget: Button to trigger project initialization
    if st.button("Initialize Project", disabled=st.session_state.project_initialized):
        with st.spinner("Simulating project initialization..."):
            # Invocation: `create_file` (mocked in Streamlit app for logging)
            # The `st.code` blocks here are for display purposes, showing typical shell commands.
            # The actual "creation" is simulated by st.info and create_file.
            st.code("!mkdir individual-air-platform\n%cd individual-air-platform\n!poetry init --name=\"individual-air-platform\" --python=\"^3.12\"")
            st.info("Simulated: `individual-air-platform` directory created and `poetry init` executed.")
            st.code('!poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx sse-starlette')
            st.info("Simulated: Core dependencies added.")
            st.code('!poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy hypothesis')
            st.info("Simulated: Development dependencies added.")
            st.code('!mkdir -p src/air/{api/routes/v1,api/routes/v2,config,models,services,schemas}\n!mkdir -p src/air/{agents,observability,mcp,events}\n!mkdir -p tests/{unit,integration,evals}\n!mkdir -p docs/{adr,requirements,failure-modes}\n!touch src/air/__init__.py')
            st.info("Simulated: Standard source directory structure created, `src/air/__init__.py` touched.")
            create_file("individual-air-platform/pyproject.toml", "[tool.poetry]\nname = \"individual-air-platform\"\nversion = \"0.1.0\"...") # Simplified content for demo
            st.success("Project initialization simulation complete!")
            
            # Update: `project_initialized` session state
            st.session_state.project_initialized = True
            # Reset subsequent steps if re-initializing
            st.session_state.settings_configured = False
            st.session_state.api_core_built = False
            st.session_state.health_checks_implemented = False

    # Display explanation after initialization
    if st.session_state.project_initialized:
        st.markdown(f"### Explanation of Execution")
        st.markdown(f"The preceding commands simulate the creation of a new Python project using Poetry and establish a well-structured directory layout.")
        st.markdown(f"- `poetry init` sets up the `pyproject.toml` file, which is the heart of our project's metadata and dependency management.")
        st.markdown(f"- `poetry add` commands populate `pyproject.toml` with our runtime and development dependencies, ensuring they are correctly versioned and installed in an isolated virtual environment.")
        st.markdown(f"- The `mkdir -p` commands create a logical, hierarchical structure for our source code, separating concerns and making the codebase easier to understand, maintain, and scale. This aligns with industry best practices for larger applications.")
        st.markdown(f"For instance, API versioning (`v1`, `v2`) is baked into the structure from the start, allowing for smooth, backward-compatible API evolution.")
        st.success("Project structure is now ready for the next steps!")

# Page: Configuration System
elif st.session_state.current_page == "2. Configuration System":
    st.title("2. Safeguarding Configuration: Pydantic Validation in Action")
    st.markdown(f"Misconfigurations are a leading cause of outages and unexpected behavior in production systems. For our AI-Readiness Platform, critical parameters — from API keys to model scoring weights — must be validated *before* the application starts. This proactive approach prevents runtime errors and ensures operational stability.")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"Consider the **Knight Capital incident** in 2012, where a single configuration deployment error led to a $440 million loss in 45 minutes. A flag intended for a \"test\" environment was mistakenly set to \"production,\" triggering unintended automated trades. Pydantic's validation-at-startup prevents such catastrophic errors by ensuring all configuration parameters meet defined constraints, failing fast with clear error messages if they don't. For our AI services, this means ensuring model weights sum correctly or API keys are present, directly impacting the reliability and safety of our AI-driven decisions.")
    st.markdown(f"Here, we define our `Settings` class using `pydantic-settings` and `Pydantic v2`. This provides a robust, type-safe, and validated configuration system, drawing values from environment variables or a `.env` file. We also include a `model_validator` to enforce complex rules, such as ensuring all scoring weights sum to 1.0.")

    st.subheader("Mathematical Explanation: Validating Scoring Weights")
    st.markdown(f"In many AI/ML applications, especially those involving composite scores or weighted features, the sum of weights must adhere to a specific constraint, often summing to 1.0. This ensures that the individual components proportionally contribute to the overall score and that the scoring logic remains consistent. If these weights deviate from their expected sum, the model's output could be skewed, leading to incorrect predictions or decisions.")
    st.markdown(r"$$ \sum_{{\small{i=1}}}^{{\small{N}}} w_i = 1.0 $$")
    st.markdown(r"where $w_i$ represents an individual scoring weight.")
    st.markdown(f"Our `model_validator` explicitly checks this condition, raising an error if the sum deviates beyond a small epsilon (e.g., $0.001$) to account for floating-point inaccuracies. This is a crucial guardrail to prevent configuration errors that could lead to invalid AI scores.")

    st.subheader("Task: Configure AI Service Settings")
    st.markdown(f"Below, you can adjust some critical scoring parameters and provide an OpenAI API key. The application will validate these settings using Pydantic.")
    
    # Layout for sliders
    st.write("---")
    st.markdown(f"**VR (Value-Readiness) Scoring Weights**")
    st.markdown(f"These weights must sum to 1.0. Adjust them and click 'Validate & Apply Settings'.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.sim_w_fluency = st.slider("W_FLUENCY", 0.0, 1.0, value=st.session_state.sim_w_fluency, step=0.01, format="%.2f")
    with col2:
        st.session_state.sim_w_domain = st.slider("W_DOMAIN", 0.0, 1.0, value=st.session_state.sim_w_domain, step=0.01, format="%.2f")
    with col3:
        st.session_state.sim_w_adaptive = st.slider("W_ADAPTIVE", 0.0, 1.0, value=st.session_state.sim_w_adaptive, step=0.01, format="%.2f")

    st.markdown(f"**Fluency Scoring Weights**")
    st.markdown(f"These weights must also sum to 1.0.")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.session_state.sim_theta_technical = st.slider("THETA_TECHNICAL", 0.0, 1.0, value=st.session_state.sim_theta_technical, step=0.01, format="%.2f")
    with col2:
        st.session_state.sim_theta_productivity = st.slider("THETA_PRODUCTIVITY", 0.0, 1.0, value=st.session_state.sim_theta_productivity, step=0.01, format="%.2f")
    with col3:
        st.session_state.sim_theta_judgment = st.slider("THETA_JUDGMENT", 0.0, 1.0, value=st.session_state.sim_theta_judgment, step=0.01, format="%.2f")
    with col4:
        st.session_state.sim_theta_velocity = st.slider("THETA_VELOCITY", 0.0, 1.0, value=st.session_state.sim_theta_velocity, step=0.01, format="%.2f")

    st.markdown(f"---")
    st.markdown(f"**LLM Provider API Key (for `SecretStr` demonstration)**")
    st.session_state.openai_api_key_configured = st.text_input("OPENAI_API_KEY", type="password", help="Enter a dummy API key to see SecretStr in action (e.g., sk-123abc...)")

    # Widget: Button to trigger settings validation and application
    if st.button("Validate & Apply Settings", disabled=not st.session_state.project_initialized):
        try:
            # Read: current_settings, sim_w_fluency, sim_w_domain, sim_w_adaptive,
            #       sim_theta_technical, sim_theta_productivity, sim_theta_judgment, sim_theta_velocity,
            #       openai_api_key_configured
            temp_settings_data = st.session_state.current_settings.model_dump()
            temp_settings_data.update({
                "W_FLUENCY": st.session_state.sim_w_fluency,
                "W_DOMAIN": st.session_state.sim_w_domain,
                "W_ADAPTIVE": st.session_state.sim_w_adaptive,
                "THETA_TECHNICAL": st.session_state.sim_theta_technical,
                "THETA_PRODUCTIVITY": st.session_state.sim_theta_productivity,
                "THETA_JUDGMENT": st.session_state.sim_theta_judgment,
                "THETA_VELOCITY": st.session_state.sim_theta_velocity,
            })
            if st.session_state.openai_api_key_configured:
                temp_settings_data["OPENAI_API_KEY"] = st.session_state.openai_api_key_configured
            else:
                temp_settings_data["OPENAI_API_KEY"] = None # Clear if input is empty

            # Invocation: `Settings` class constructor (triggers `model_validator`)
            new_settings = Settings(**temp_settings_data)
            
            # Update: `current_settings`, `settings_configured` session state
            st.session_state.current_settings = new_settings
            st.session_state.settings_configured = True
            st.success("Settings validated and applied successfully!")
            st.json(st.session_state.current_settings.model_dump_json(indent=2))
            st.info(f"OpenAI API Key (masked by SecretStr): {st.session_state.current_settings.OPENAI_API_KEY}")

        except ValueError as e:
            st.error(f"Configuration Validation Error: {e}")
            st.session_state.settings_configured = False
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.settings_configured = False

    if st.session_state.settings_configured:
        st.markdown(f"### Explanation of Execution")
        st.markdown(f"We've successfully defined our `Settings` class, which uses Pydantic to validate configuration parameters. When `Settings()` is called (even with updated values), Pydantic performs immediate validation based on the types, bounds (`Field(ge=..., le=...)`), and custom `model_validator` functions (e.g., `validate_weight_sums`).")
        st.markdown(f"- The VR and Fluency scoring parameters are loaded and their sums are validated. This ensures that any AI scoring logic relying on these weights will operate with consistent and valid inputs, preventing the kind of \"garbage in, garbage out\" scenarios that can undermine AI system reliability.")
        st.markdown(f"- `SecretStr` for `OPENAI_API_KEY` prevents sensitive information from being accidentally printed or exposed, as seen in the masked output above.")
        st.markdown(f"This system acts as an early warning mechanism, catching configuration issues at application startup rather than letting them cause silent failures or incorrect AI decisions later in the workflow.")

# Page: API Core & Middleware
elif st.session_state.current_page == "3. API Core & Middleware":
    st.title("3. Building the API Core: Versioned Routers and Middleware")
    st.markdown(f"As the Software Developer, your task is to construct the FastAPI application, integrating versioned API routes and crucial middleware for cross-cutting concerns. This setup ensures our AI service is not only functional but also maintainable, observable, and adaptable to future changes. The \"Application Factory Pattern\" allows us to create multiple FastAPI app instances, useful for testing or different deployment contexts.")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"A production-ready AI service must handle various operational requirements beyond just serving model predictions.")
    st.markdown(f"- **API Versioning:** As AI models evolve, so do their APIs. Versioned routers (`/api/v1`, `/api/v2`) ensure backward compatibility, allowing seamless upgrades for clients without disrupting existing integrations. This is crucial for an \"Individual AI-Readiness Platform\" that will continuously evolve its capabilities.")
    st.markdown(f"- **Middleware:** Cross-cutting concerns like CORS (Cross-Origin Resource Sharing), request timing, and request ID tracking are essential for web services.")
    st.markdown(f"    - **CORS Middleware** allows frontend applications (e.g., a dashboard for the AI platform) to securely interact with our backend API.")
    st.markdown(f"    - **Request Timing Middleware** provides crucial performance metrics. By attaching an `X-Process-Time` header to every response, we enable monitoring systems to track API latency, a key indicator of service health and user experience.")
    st.markdown(f"    - **Request ID Middleware** assigns a unique ID (`X-Request-ID`) to each request. This ID is vital for tracing requests through complex microservice architectures, especially when debugging issues across multiple services in a production environment.")
    st.markdown(f"- **Exception Handling:** Graceful error handling, especially for validation errors, provides informative feedback to API consumers, making the service more user-friendly and robust.")

    st.subheader("Action: Simulate API Core Build")
    st.markdown(f"Click the button to simulate the construction of the FastAPI application with its middleware and routers. This will demonstrate the structure and logging of the application factory pattern.")
    
    # Widget: Button to simulate API core build
    if st.button("Build API Core", disabled=not st.session_state.settings_configured or st.session_state.api_core_built):
        with st.spinner("Building FastAPI application core..."):
            # Invocation: Simulating `create_app_notebook()` and `lifespan_notebook` execution
            # We cannot run an actual FastAPI server, so we simulate the print output
            st.info("Simulating `create_app_notebook()` and `lifespan_notebook` execution and its initial logs...")
            
            # Use an f-string to dynamically generate the code block for display,
            # ensuring the embedded f-strings (e.g., f" - GET {settings.API_V1_PREFIX}/items")
            # are correctly shown as Python code.
            settings = st.session_state.current_settings
            st.code(f"""
# Simplified simulation of create_app_notebook() startup logs
print("🚀 Starting {{settings.APP_NAME}} v{{settings.APP_VERSION}}")
print("🌍 Environment: {{settings.APP_ENV}}")
print("🔢 Parameter Version: {{settings.parameter_version}}")
print("🛡️ Guardrails: {{'Enabled' if settings.GUARDRAILS_ENABLED else 'Disabled'}}")
print("💰 Cost Budget: ${{settings.DAILY_COST_BUDGET_USD}}/day")
setup_tracing(app) # Simulated call
print("Initializing observability tracing (simulated)...")
print("Application initialized with routers:")
print(f"  - GET {{settings.API_V1_PREFIX}}/items")
print(f"  - GET {{settings.API_V2_PREFIX}}/items")
print("Middleware applied: CORS, Request ID, Request Timing.")
print("Exception handlers for ValueError, HTTPException registered.")
            """)
            st.success("FastAPI application core simulated successfully!")
            
            # Update: `api_core_built` session state
            st.session_state.api_core_built = True

    if st.session_state.api_core_built:
        st.markdown(f"### Explanation of Execution")
        st.markdown(f"The `create_app_notebook()` function demonstrates the \"Application Factory Pattern\" by returning a fully configured FastAPI application instance.")
        st.markdown(f"- The `lifespan_notebook` context manager ensures that startup (e.g., observability initialization) and shutdown tasks are handled gracefully.")
        st.markdown(f"- `CORSMiddleware` is added, crucial for allowing web clients to interact with our API securely.")
        st.markdown(f"- The custom `add_request_context_notebook` middleware successfully injects a unique `X-Request-ID` and `X-Process-Time` header into responses. This is vital for distributed tracing and performance monitoring.")
        st.markdown(f"- The exception handlers for `ValueError` and `HTTPException` are registered, providing standardized and informative error responses.")
        st.markdown(f"- Finally, the versioned routers (`/api/v1/items`, `/api/v2/items`) are included, demonstrating how different API versions can coexist, enabling the platform to evolve its AI capabilities without breaking existing client integrations.")
        st.markdown(f"The simulated startup confirms that all these components are correctly initialized and registered within the FastAPI application.")

# Page: Health Checks
elif st.session_state.current_page == "4. Health Checks":
    st.title("4. Ensuring Service Reliability: Comprehensive Health Checks")
    st.markdown(f"For any production AI service, merely having the API running isn't enough; we need to know if it's truly *healthy* and capable of serving requests. This means checking not only the application itself but also all its critical dependencies like databases, caching layers (Redis), and external LLM APIs. Robust health checks are vital for automated monitoring, load balancing, and self-healing systems in containerized environments like Kubernetes.")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"As a Software Developer, implementing detailed health checks is crucial for ensuring the AI-Readiness Platform's uptime and reliability. Imagine a scenario where your AI model relies on a database for feature storage and an external LLM API for inference. If the database is down, or the LLM API is unreachable, your service might technically be \"running\" but unable to perform its core function.")
    st.markdown(f"- **`/health` (Basic Health):** A fast check for basic application responsiveness, used by load balancers.")
    st.markdown(f"- **`/health/detailed` (Detailed Health):** Provides an in-depth status of all internal and external dependencies. This allows operators to quickly diagnose issues. For example, if the `check_llm()` indicates a \"degraded\" status due to high latency, it immediately points to a potential external API issue impacting our AI service's performance.")
    st.markdown(f"- **`/health/ready` (Readiness Probe):** Tells container orchestrators (like Kubernetes) if the service is ready to accept traffic. If dependencies are unhealthy, the service shouldn't receive requests.")
    st.markdown(f"- **`/health/live` (Liveness Probe):** Indicates if the application is still running and hasn't frozen. If this fails, the container needs to be restarted.")
    st.markdown(f"These checks are fundamental for maintaining service level agreements (SLAs) and ensuring our AI services are always operational.")

    st.subheader("Task: Test Health Check Endpoints")
    st.markdown(f"Use the controls below to simulate the health status of external dependencies and observe how the application's health checks respond.")

    if not st.session_state.api_core_built:
        st.warning("Please complete the '3. API Core & Middleware' step first to unlock health checks.")
    else:
        st.write("---")
        st.markdown("**Simulate Dependency Status:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            # Widget: Selectbox for simulated database status
            st.session_state.simulated_db_status = st.selectbox("Database Status", ["healthy", "degraded", "unhealthy"], index=["healthy", "degraded", "unhealthy"].index(st.session_state.simulated_db_status), key="db_status_select")
        with col2:
            # Widget: Selectbox for simulated Redis status
            st.session_state.simulated_redis_status = st.selectbox("Redis Status", ["healthy", "degraded", "unhealthy"], index=["healthy", "degraded", "unhealthy"].index(st.session_state.simulated_redis_status), key="redis_status_select")
        with col3:
            # Widget: Selectbox for simulated LLM status
            st.session_state.simulated_llm_status = st.selectbox("LLM API Status", ["healthy", "degraded", "unhealthy"], index=["healthy", "degraded", "unhealthy"].index(st.session_state.simulated_llm_status), key="llm_status_select")
            # Read: `current_settings.OPENAI_API_KEY`
            if not st.session_state.current_settings.OPENAI_API_KEY:
                st.info("LLM API status will reflect 'not_configured' as no API key is set.")

        # Widget: Button to run health checks
        if st.button("Run Health Checks"):
            # Update: `health_checks_implemented` session state
            st.session_state.health_checks_implemented = True
            with st.spinner("Running health checks..."):
                # Read: `current_settings`, `simulated_db_status`, `simulated_redis_status`, `simulated_llm_status`, `openai_api_key_configured`
                
                # Invocation: `health_check_func_st`
                basic_health_result = asyncio.run(health_check_func_st(st.session_state.current_settings))
                st.subheader("Basic Health Check (`/health`)")
                st.json(basic_health_result.model_dump_json(indent=2))

                # Invocation: `detailed_health_check_func_st`
                detailed_health_result = asyncio.run(
                    detailed_health_check_func_st(
                        st.session_state.current_settings,
                        st.session_state.simulated_db_status,
                        st.session_state.simulated_redis_status,
                        st.session_state.simulated_llm_status,
                        st.session_state.current_settings.OPENAI_API_KEY.get_secret_value() if st.session_state.current_settings.OPENAI_API_KEY else None
                    )
                )
                # Update: `last_health_response` session state
                st.session_state.last_health_response = detailed_health_result
                st.subheader("Detailed Health Check (`/health/detailed`)")
                st.json(st.session_state.last_health_response.model_dump_json(indent=2))

                # Invocation: `readiness_check_func_st`
                readiness_result, readiness_status_code = asyncio.run(
                    readiness_check_func_st(
                        st.session_state.current_settings,
                        st.session_state.simulated_db_status,
                        st.session_state.simulated_redis_status,
                        st.session_state.simulated_llm_status,
                        st.session_state.current_settings.OPENAI_API_KEY.get_secret_value() if st.session_state.current_settings.OPENAI_API_KEY else None
                    )
                )
                st.subheader("Readiness Probe (`/health/ready`)")
                if readiness_status_code == 200:
                    st.success(f"Status: {readiness_result['status']}")
                else:
                    st.error(f"Status: {readiness_result['status']} (Code: {readiness_status_code}) - {readiness_result['reason']}")
                st.json(readiness_result)

                # Invocation: `liveness_check_func_st`
                liveness_result, liveness_status_code = asyncio.run(liveness_check_func_st())
                st.subheader("Liveness Probe (`/health/live`)")
                st.success(f"Status: {liveness_result['status']} (Code: {liveness_status_code})")
                st.json(liveness_result)

        if st.session_state.health_checks_implemented:
            st.markdown(f"### Explanation of Execution")
            st.markdown(f"The execution demonstrates the functionality of our comprehensive health check endpoints:")
            st.markdown(f"- The `/health` endpoint provides a quick, basic check of the application's version, environment, and current timestamp, confirming the service process is responsive.")
            st.markdown(f"- The `/health/detailed` endpoint concurrently checks all configured dependencies (database, Redis, LLM API using `asyncio.gather`). It aggregates their individual statuses and latencies to determine an overall service health, providing granular insights crucial for troubleshooting.")
            st.markdown(f"- The `/health/ready` endpoint indicates if the service is prepared to receive traffic, taking into account the health of its critical dependencies. You observed that if a dependency is \"unhealthy\" or \"degraded\" (or \"not_configured\" for LLM without a key), this probe fails, instructing orchestrators to not route traffic to this instance.")
            st.markdown(f"- The `/health/live` endpoint confirms the application is active and hasn't crashed, allowing orchestrators to restart it if unresponsive.")
            st.markdown(f"These endpoints provide the essential observability for the AI-Readiness Platform, enabling automated systems to ensure high availability and rapid detection of operational issues.")

# Page: Common Pitfalls & Best Practices
elif st.session_state.current_page == "5. Common Pitfalls & Best Practices":
    st.title("5. Avoiding Common Pitfalls: Best Practices in Action")
    st.markdown(f"As a Software Developer, understanding and proactively addressing common mistakes is just as important as implementing new features. This section reviews critical configuration and application setup pitfalls, demonstrating how the patterns we've adopted (like Pydantic validation and FastAPI's `lifespan` manager) help prevent them. This hands-on review reinforces best practices for building robust and secure AI services.")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"Ignoring best practices often leads to hidden bugs, security vulnerabilities, or catastrophic failures in production. For an AI service, this could mean incorrect model predictions due to bad configurations, data breaches from exposed secrets, or resource leaks that degrade performance over time. By explicitly addressing these \"common mistakes,\" we ensure that the Individual AI-Readiness Platform adheres to high standards of reliability, security, and maintainability, protecting both our data and our reputation.")

    st.subheader("Review: Common Mistakes & Troubleshooting")
    st.markdown(f"Let's review how our current architecture prevents critical issues.")

    st.write("---")
    st.markdown(f"### Mistake 1: Not validating weight sums")
    st.markdown(f"**PROBLEM**: Configuration allows weights that don't sum to 1.0, leading to incorrect AI scoring.")
    st.markdown(f"**WRONG Example (if validation was absent):**")
    st.code(f"""
W_FLUENCY_WRONG = 0.50
W_DOMAIN_WRONG = 0.40
W_ADAPTIVE_WRONG = 0.20 # Sum = 1.10, which is incorrect!
# This would be loaded without error and cause subtle AI model issues.
    """)
    st.markdown(f"**FIX**: Pydantic's `model_validator` catches this at startup.")
    st.markdown(f"As demonstrated in the **Configuration System** page, if you tried to set weights that don't sum to 1.0, Pydantic immediately raises a `ValueError`. This \"fail-fast\" mechanism prevents the application from even starting with an valid configuration.")
    # Read: current_settings
    st.success(f"Current configuration is valid. VR Sum: {st.session_state.current_settings.W_FLUENCY + st.session_state.current_settings.W_DOMAIN + st.session_state.current_settings.W_ADAPTIVE:.2f}, Fluency Sum: {st.session_state.current_settings.THETA_TECHNICAL + st.session_state.current_settings.THETA_PRODUCTIVITY + st.session_state.current_settings.THETA_JUDGMENT + st.session_state.current_settings.THETA_VELOCITY:.2f}")


    st.write("---")
    st.markdown(f"### Mistake 2: Exposing secrets in logs")
    st.markdown(f"**PROBLEM**: Sensitive API keys or credentials are logged directly, creating a security vulnerability.")
    st.markdown(f"**WRONG Example**: Logging the actual API key directly.")
    st.code(f"""
dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
print(f"Using key: {{dummy_api_key}}") # This prints the full key!
    """)
    st.markdown(f"**FIX**: Use Pydantic's `SecretStr`. It masks values upon string conversion.")
    st.markdown(f"As you saw in the **Configuration System** page, when you entered an OpenAI API key, it was displayed in a masked format (e.g., `**********`).")
    # Read: current_settings.OPENAI_API_KEY
    st.info(f"OpenAI API Key in current settings (masked by SecretStr): {st.session_state.current_settings.OPENAI_API_KEY}")
    st.markdown(f"This ensures that sensitive information is not accidentally exposed in logs or console output, significantly enhancing the security posture of the AI service.")

    st.write("---")
    st.markdown(f"### Mistake 3: Missing lifespan context manager")
    st.markdown(f"**PROBLEM**: Resources (database connections, thread pools) are not properly cleaned up on application shutdown, leading to leaks.")
    st.markdown(f"**WRONG Example**: FastAPI app without a lifespan context manager.")
    st.code(f"""
# app = FastAPI()
# # Resources leak on shutdown!
# print("FastAPI app initialized without lifespan. (Resources would leak!)")
    """)
    st.markdown(f"**FIX**: Always use `asynccontextmanager` for FastAPI's `lifespan`.")
    st.markdown(f"Our simulated API Core build included `lifespan_notebook`. This ensures that `setup_tracing` (and other cleanup operations) are correctly called during application startup and shutdown.")
    st.success("The `lifespan_notebook` is designed to handle graceful startup and shutdown, preventing resource leaks.")

    st.markdown(f"### Explanation of Execution")
    st.markdown(f"This section actively demonstrates how implementing robust practices prevents common errors:")
    st.markdown(f"1.  **Weight Sum Validation:** You experienced that Pydantic's `model_validator` immediately raises a `ValueError` for incorrect weights. This \"fail-fast\" mechanism prevents the AI service from starting with invalid parameters that could lead to incorrect model behavior, fulfilling the goal of preventing Knight Capital-like configuration errors.")
    st.markdown(f"2.  **Secret Handling:** By using `SecretStr` for `OPENAI_API_KEY`, the output shows that the sensitive key is masked. This is a critical security measure for the AI-Readiness Platform, preventing accidental exposure of credentials in logs, console output, or error reports, significantly reducing the risk of data breaches.")
    st.markdown(f"3.  **Lifespan Management:** The simulated startup and shutdown using the `lifespan_notebook` context manager visually confirms that explicit startup and shutdown routines are executed. This ensures that resources like database connections, caching clients, or tracing exporters are properly initialized when the AI service starts and gracefully closed when it shuts down, preventing resource leaks and ensuring application stability over its lifecycle.")
    st.markdown(f"By embracing these best practices, we ensure that the AI services built for the Individual AI-Readiness Platform are not only performant but also secure, reliable, and maintainable in a production environment.")


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
