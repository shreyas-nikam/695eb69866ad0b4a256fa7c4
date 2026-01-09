

import streamlit as st
import asyncio
import os
from datetime import datetime
from source import *

# --- Page Config ---
st.set_page_config(page_title="QuLab: Foundation & Platform Setup", layout="wide")
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
    original_env_vars = {}
    for var in ['W_FLUENCY', 'W_DOMAIN', 'W_ADAPTIVE']:
        if var in os.environ:
            original_env_vars[var] = os.environ[var]
    
    os.environ['W_FLUENCY'] = '0.5'
    os.environ['W_DOMAIN'] = '0.4'
    os.environ['W_ADAPTIVE'] = '0.2' # Sum = 1.10, incorrect

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
    original_openai_api_key = os.environ.get('OPENAI_API_KEY')
    dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    os.environ['OPENAI_API_KEY'] = dummy_api_key
    
    # Instantiate Settings to pick up the new env var
    temp_settings = get_settings() # Use get_settings to ensure caching/defaults are handled
    masked_key = str(temp_settings.OPENAI_API_KEY) if temp_settings.OPENAI_API_KEY else "Not configured."
    key_type = str(type(temp_settings.OPENAI_API_KEY)) if temp_settings.OPENAI_API_KEY else "NoneType"
    
    # Clean up and restore
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    if original_openai_api_key is not None:
        # FIX: The variable 'var' was undefined. It should be 'OPENAI_API_KEY'.
        os.environ['OPENAI_API_KEY'] = original_openai_api_key 

    return f"OpenAI API Key (using SecretStr): {masked_key}\nType of key: {key_type}"

async def simulate_app_lifespan_output_async(app_instance, settings_obj):
    """Simulates the startup and shutdown of the FastAPI app using its lifespan."""
    messages = []
    messages.append(f"🚀 Starting {settings_obj.APP_NAME} v{settings_obj.APP_VERSION}")
    messages.append(f"🌍 Environment: {settings_obj.APP_ENV}")
    messages.append(f"🔢 Parameter Version: {settings_obj.parameter_version}")
    messages.append(f"🛡️ Guardrails: {'Enabled' if settings_obj.GUARDRAILS_ENABLED else 'Disabled'}")
    messages.append(f"💰 Cost Budget: ${settings_obj.DAILY_COST_BUDGET_USD}/day")
    if not settings_obj.DEBUG:
        messages.append(setup_tracing(app_instance)) # setup_tracing is imported from source
    messages.append("    Application started up (resources initialized).")
    await asyncio.sleep(0.05) # Simulate some runtime
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
    st.markdown(f"**Action**: In a real scenario, you would run `pip install fastapi 'uvicorn[standard]' pydantic pydantic-settings httpx sse-starlette` to get the core dependencies.")
    st.success("Dependencies assumed to be installed for this interactive lab environment.")

elif st.session_state.current_page == 'Task 1.1: Project Initialization':
    st.header("2. Project Kick-off: Laying the Foundation for the AI-Readiness Platform")
    st.markdown(f"As a Software Developer at the Individual AI-Readiness Platform, your first major task is to establish a standardized project structure and manage dependencies effectively. This isn't just about organizing files; it's about enforcing consistency across all AI services, streamlining onboarding for new developers, and ensuring predictable behavior in development and production environments. We'll use Poetry to manage dependencies and define a clear directory layout tailored for an API-driven AI service.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"A well-defined project structure and dependency management system reduce technical debt, prevent dependency conflicts, and accelerate development cycles. For an organization like ours, this means a more reliable AI platform and faster iteration on new AI capabilities.")
    st.markdown(f"---")
    st.markdown(f"### Task: Project Initialization and Structure Setup")
    st.markdown(f"We're starting a new AI service within the Individual AI-Readiness Platform. To ensure a consistent and maintainable codebase from day one, we'll initialize a new Python project using Poetry and establish a standard project directory structure. This structure will accommodate various components like API routes, configuration, models, and services, making our project scalable and easy to navigate for any developer joining the team.")
    st.markdown(f"")
    st.markdown(f"Poetry helps us manage dependencies, create isolated virtual environments, and build distributable packages, which is crucial for moving our service from development to production seamlessly.")

    # Widget: Button to simulate project initialization
    if st.button("Simulate Project Initialization"):
        st.session_state.project_init_output = simulate_project_initialization_output()
        st.success("Project Initialization Simulated!")
    
    # Display output if available in session state
    if st.session_state.project_init_output:
        st.markdown(f"### Simulated Output:")
        st.code(st.session_state.project_init_output, language='bash')
        st.markdown(f"### Explanation of Execution")
        st.markdown(f"The preceding commands simulate the creation of a new Python project using Poetry and establish a well-structured directory layout.")
        st.markdown(f"- `poetry init` sets up the `pyproject.toml` file, which is the heart of our project's metadata and dependency management.")
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
    st.markdown(r"where $w_i$ represents the $i$-th scoring weight and $N$ is the total number of weights.")
    st.markdown(r"Our `model_validator` explicitly checks this condition, raising an error if the sum deviates beyond a small epsilon (e.g., $0.001$) to account for floating-point inaccuracies. This is a crucial guardrail to prevent configuration errors that could lead to invalid AI scores.")
    st.markdown(f"---")
    st.markdown(f"### Task: Implement a Configuration System with Full Validation")
    st.markdown(f"We are setting up the core configuration for our AI service. This includes application details, API prefixes, database URLs, LLM provider keys, and crucial scoring parameters. To prevent configuration-related failures, we'll use Pydantic-Settings for strong type validation and enforce business rules like ensuring scoring weights sum to 1.0. This ensures the integrity of our AI model's parameters and the overall stability of the service.")
    st.markdown(f"")
    st.markdown(f"The use of `SecretStr` for API keys adds a layer of security by preventing accidental logging of sensitive information.")

    # Widget: Button to load and validate settings
    if st.button("Load and Validate Settings"):
        st.session_state.settings_object = get_settings() # Call the function from source.py
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
        st.markdown(f"- `SecretStr` for `OPENAI_API_KEY` prevents sensitive information from being accidentally printed or exposed.")
        st.markdown(f"- The output shows that our scoring parameters, like `W_FLUENCY`, `W_DOMAIN`, and `W_ADAPTIVE`, are loaded correctly, and their sum is validated. This ensures that any AI scoring logic relying on these weights will operate with consistent and valid inputs, preventing the kind of 'garbage in, garbage out' scenarios that can undermine AI system reliability.")
        st.markdown(f"This system acts as an early warning mechanism, catching configuration issues at application startup rather than letting them cause silent failures or incorrect AI decisions later in the workflow.")
    else:
        st.info("Click 'Load and Validate Settings' to see the configuration system in action.")

elif st.session_state.current_page == 'Task 1.3: FastAPI Application':
    st.header("4. Building the API Core: Versioned Routers and Middleware")
    st.markdown(f"As the Software Developer, your task is to construct the FastAPI application, integrating versioned API routes and crucial middleware for cross-cutting concerns. This setup ensures our AI service is not only functional but also maintainable, observable, and adaptable to future changes. The 'Application Factory Pattern' allows us to create multiple FastAPI app instances, useful for testing or different deployment contexts.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"A production-ready AI service must handle various operational requirements beyond just serving model predictions.")
    st.markdown(f"- **API Versioning:** As AI models evolve, so do their APIs. Versioned routers (`/api/v1`, `/api/v2`) ensure backward compatibility, allowing seamless upgrades for clients without disrupting existing integrations. This is crucial for an 'Individual AI-Readiness Platform' that will continuously evolve its capabilities.")
    st.markdown(f"- **Middleware:** Cross-cutting concerns like CORS (Cross-Origin Resource Sharing), request timing, and request ID tracking are essential for web services.")
    st.markdown(f"    - **CORS Middleware** allows frontend applications (e.g., a dashboard for the AI platform) to securely interact with our backend API.")
    st.markdown(f"    - **Request Timing Middleware** provides crucial performance metrics. By attaching an `X-Process-Time` header to every response, we enable monitoring systems to track API latency, a key indicator of service health and user experience.")
    st.markdown(f"    - **Request ID Middleware** assigns a unique ID (`X-Request-ID`) to each request. This ID is vital for tracing requests through complex microservice architectures, especially when debugging issues across multiple services in a production environment.")
    st.markdown(f"- **Exception Handling:** Graceful error handling, especially for validation errors, provides informative feedback to API consumers, making the service more user-friendly and robust.")
    st.markdown(f"---")
    st.markdown(f"### Task: Implement FastAPI Application with Versioned Routers and Middleware")
    st.markdown(f"Now we will build the main FastAPI application. This involves:")
    st.markdown(f"1. Defining a `lifespan` context manager for startup and shutdown events (e.g., initializing tracing).")
    st.markdown(f"2. Implementing an 'Application Factory Pattern' (`create_app`) to create FastAPI instances.")
    st.markdown(f"3. Adding `CORSMiddleware` to handle cross-origin requests securely.")
    st.markdown(f"4. Implementing a custom HTTP middleware to inject a unique request ID and track request processing time.")
    st.markdown(f"5. Defining global exception handlers for better error reporting.")
    st.markdown(f"6. Including versioned API routers (`v1_router`, `v2_router`) and a dedicated health router.")
    st.markdown(f"")
    st.markdown(f"This setup ensures our AI service is robust, secure, observable, and ready for continuous deployment.")

    if st.session_state.settings_object is None:
        st.warning("Please complete 'Task 1.2: Configuration System' first to load application settings.")
    else:
        # Widget: Button to create FastAPI application
        if st.button("Create FastAPI Application"):
            # Call the app factory from source.py, passing settings from session state
            app_instance = create_app_notebook(st.session_state.settings_object)
            st.session_state.fastapi_app_object = app_instance

            # Simulate app startup/shutdown
            sim_output = asyncio.run(
                simulate_app_lifespan_output_async(st.session_state.fastapi_app_object, st.session_state.settings_object)
            )
            st.session_state.fastapi_app_output = sim_output
            st.success("FastAPI Application created and startup simulated!")
        
        # Display output if available in session state
        if st.session_state.fastapi_app_output:
            st.markdown(f"### Simulated Application Startup and Router Inclusion:")
            st.code(st.session_state.fastapi_app_output, language='bash')
            st.markdown(f"App initialized with routes: ")
            st.markdown(f"- GET /health")
            st.markdown(f"- GET {st.session_state.settings_object.API_V1_PREFIX}/items")
            st.markdown(f"- GET {st.session_state.settings_object.API_V2_PREFIX}/items")
            st.markdown(f"- GET {st.session_state.settings_object.API_V1_PREFIX}/raise-value-error (for demo)")
            st.markdown(f"- GET {st.session_state.settings_object.API_V1_PREFIX}/raise-http-exception/{{status_code}} (for demo)")
            st.markdown(f"Application is running (simulated).\n")

            st.markdown(f"### Explanation of Execution")
            st.markdown(f"The `create_app_notebook()` function demonstrates the 'Application Factory Pattern' by returning a fully configured FastAPI application instance.")
            st.markdown(f"- The `lifespan_notebook` context manager ensures that startup (e.g., observability initialization) and shutdown tasks are handled gracefully. (Simulated in output)")
            st.markdown(f"- `CORSMiddleware` is added, crucial for allowing web clients to interact with our API securely.")
            st.markdown(f"- The custom `add_request_context_notebook` middleware successfully injects a unique `X-Request-ID` and `X-Process-Time` header into responses. This is vital for distributed tracing and performance monitoring.")
            st.markdown(f"- The exception handlers for `ValueError` and `HTTPException` are registered, providing standardized and informative error responses.")
            st.markdown(f"- Finally, the versioned routers (`/api/v1/items`, `/api/v2/items`) are included, demonstrating how different API versions can coexist, enabling the platform to evolve its AI capabilities without breaking existing client integrations.")
            st.markdown(f"The simulated startup confirms that all these components are correctly initialized and registered within the FastAPI application.")
        else:
            st.info("Click 'Create FastAPI Application' to build and simulate the app startup.")

elif st.session_state.current_page == 'Task 1.4: Health Check':
    st.header("5. Ensuring Service Reliability: Comprehensive Health Checks")
    st.markdown(f"For any production AI service, merely having the API running isn't enough; we need to know if it's truly *healthy* and capable of serving requests. This means checking not only the application itself but also all its critical dependencies like databases, caching layers (Redis), and external LLM APIs. Robust health checks are vital for automated monitoring, load balancing, and self-healing systems in containerized environments like Kubernetes.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"As a Software Developer, implementing detailed health checks is crucial for ensuring the AI-Readiness Platform's uptime and reliability. Imagine a scenario where your AI model relies on a database for feature storage and an external LLM API for inference. If the database is down, or the LLM API is unreachable, your service might technically be 'running' but unable to perform its core function.")
    st.markdown(f"- **`/health` (Basic Health):** A fast check for basic application responsiveness, used by load balancers.")
    st.markdown(f"- **`/health/detailed` (Detailed Health):** Provides an in-depth status of all internal and external dependencies. This allows operators to quickly diagnose issues. For example, if the `check_llm()` indicates a 'degraded' status due to high latency, it immediately points to a potential external API issue impacting our AI service's performance.")
    st.markdown(f"- **`/health/ready` (Readiness Probe):** Tells container orchestrators (like Kubernetes) if the service is ready to accept traffic. If dependencies are unhealthy, the service shouldn't receive requests.")
    st.markdown(f"- **`/health/live` (Liveness Probe):** Indicates if the application is still running and hasn't frozen. If this fails, the container needs to be restarted.")
    st.markdown(f"These checks are fundamental for maintaining service level agreements (SLAs) and ensuring our AI services are always operational.")
    st.markdown(f"---")
    st.markdown(f"### Task: Implement Comprehensive Health Check Endpoints with Dependency Status")
    st.markdown(f"We need to add health check endpoints to our API. These endpoints will provide insights into the application's status and its critical dependencies. This involves:")
    st.markdown(f"1. Defining Pydantic models for `DependencyStatus`, `HealthResponse`, and `DetailedHealthResponse`.")
    st.markdown(f"2. Implementing asynchronous functions to simulate checks for external dependencies (database, Redis, LLM).")
    st.markdown(f"3. Creating API endpoints for basic health (`/health`), detailed health (`/health/detailed`), readiness (`/health/ready`), and liveness (`/health/live`).")
    st.markdown(f"")
    st.markdown(f"These checks are crucial for reliable deployments and operational monitoring in a production AI environment.")

    if st.session_state.settings_object is None or st.session_state.fastapi_app_object is None:
        st.warning("Please complete 'Task 1.2: Configuration System' and 'Task 1.3: FastAPI Application' first.")
    else:
        st.subheader("Run Health Checks")
        col1, col2 = st.columns(2)
        with col1:
            # Widget: Button to run basic health check
            if st.button("Run Basic Health Check (/health)"):
                st.session_state.basic_health_output = asyncio.run(health_check_func(st.session_state.settings_object)).model_dump_json(indent=2)
                st.success("Basic Health Check Completed!")
            # Display output if available
            if st.session_state.basic_health_output:
                st.markdown("Output of `/health`:")
                st.code(st.session_state.basic_health_output, language='json')
        
        with col2:
            # Widget: Button to run detailed health check
            if st.button("Run Detailed Health Check (/health/detailed)"):
                st.session_state.detailed_health_output = asyncio.run(detailed_health_check_func(st.session_state.settings_object)).model_dump_json(indent=2)
                st.success("Detailed Health Check Completed!")
            # Display output if available
            if st.session_state.detailed_health_output:
                st.markdown("Output of `/health/detailed`:")
                st.code(st.session_state.detailed_health_output, language='json')

        col3, col4 = st.columns(2)
        with col3:
            # Widget: Button to run readiness probe
            if st.button("Run Readiness Probe (/health/ready)"):
                status_content, status_code = asyncio.run(readiness_check_func(st.session_state.settings_object))
                st.session_state.readiness_output = f"Status Code: {status_code}\nContent: {status_content}"
                if status_code == 200:
                    st.success("Readiness Probe Completed: Service is Ready!")
                else:
                    st.error(f"Readiness Probe Failed (Status {status_code}): Service is Not Ready!")
            # Display output if available
            if st.session_state.readiness_output:
                st.markdown("Output of `/health/ready`:")
                st.code(st.session_state.readiness_output, language='plaintext')

        with col4:
            # Widget: Button to run liveness probe
            if st.button("Run Liveness Probe (/health/live)"):
                status_content, status_code = asyncio.run(liveness_check_func())
                st.session_state.liveness_output = f"Status Code: {status_code}\nContent: {status_content}"
                if status_code == 200:
                    st.success("Liveness Probe Completed: Service is Alive!")
                else:
                    st.error(f"Liveness Probe Failed (Status {status_code}): Service is Not Alive!")
            # Display output if available
            if st.session_state.liveness_output:
                st.markdown("Output of `/health/live`:")
                st.code(st.session_state.liveness_output, language='plaintext')
        
        if st.session_state.detailed_health_output or st.session_state.basic_health_output:
            st.markdown(f"### Explanation of Execution")
            st.markdown(f"The execution demonstrates the functionality of our comprehensive health check endpoints:")
            st.markdown(f"- The `/health` endpoint provides a quick, basic check of the application's version, environment, and current timestamp, confirming the service process is responsive.")
            st.markdown(f"- The `/health/detailed` endpoint concurrently checks all configured dependencies (database, Redis, LLM API using `asyncio.gather`). It aggregates their individual statuses and latencies to determine an overall service health, providing granular insights crucial for troubleshooting.")
            st.markdown(f"- The `/health/ready` endpoint indicates if the service is prepared to receive traffic, taking into account the health of its critical dependencies. In our simulation, it returns 'ready' as all dependencies are marked 'healthy' or 'not_configured' (which is treated as degraded in this context, but not 'unhealthy'). If a dependency were 'unhealthy,' this probe would fail, instructing orchestrators to not route traffic to this instance.")
            st.markdown(f"- The `/health/live` endpoint confirms the application is active and hasn't crashed, allowing orchestrators to restart it if unresponsive.")
            st.markdown(f"")
            st.markdown(f"These endpoints provide the essential observability for the AI-Readiness Platform, enabling automated systems to ensure high availability and rapid detection of operational issues.")

elif st.session_state.current_page == 'Common Mistakes & Troubleshooting':
    st.header("6. Avoiding Common Pitfalls: Best Practices in Action")
    st.markdown(f"As a Software Developer, understanding and proactively addressing common mistakes is just as important as implementing new features. This section reviews critical configuration and application setup pitfalls, demonstrating how the patterns we've adopted (like Pydantic validation and FastAPI's `lifespan` manager) help prevent them. This hands-on review reinforces best practices for building robust and secure AI services.")
    st.markdown(f"")
    st.markdown(f"### Why this matters (Real-world relevance)")
    st.markdown(f"Ignoring best practices often leads to hidden bugs, security vulnerabilities, or catastrophic failures in production. For an AI service, this could mean incorrect model predictions due to bad configurations, data breaches from exposed secrets, or resource leaks that degrade performance over time. By explicitly addressing these 'common mistakes,' we ensure that the Individual AI-Readiness Platform adheres to high standards of reliability, security, and maintainability, protecting both our data and our reputation.")
    st.markdown(f"---")
    st.markdown(f"### Task: Review Common Mistakes & Troubleshooting")
    st.markdown(f"We will examine common errors in setting up production-ready services and demonstrate how our current architecture prevents them. This includes:")
    st.markdown(f"1. **Mistake 1: Not validating weight sums:** How Pydantic's `model_validator` catches this at startup.")
    st.markdown(f"2. **Mistake 2: Exposing secrets in logs:** How Pydantic's `SecretStr` masks sensitive values.")
    st.markdown(f"3. **Mistake 3: Missing lifespan context manager:** Why `asynccontextmanager` is crucial for resource cleanup.")
    st.markdown(f"")
    st.markdown(f"Understanding these common pitfalls and their solutions is essential for building truly resilient AI services.")

    st.subheader("Mistake 1: Not validating weight sums")
    st.markdown(f"**PROBLEM**: Configuration allows weights that don't sum to 1.0, leading to incorrect AI scoring.")
    st.markdown(f"**WRONG Example (if validation was absent):**")
    st.code(f"""
# Imagine these values are read from an .env file without Pydantic validation
W_FLUENCY_WRONG = 0.50
W_DOMAIN_WRONG = 0.40
W_ADAPTIVE_WRONG = 0.20 # Sum = 1.10, which is incorrect!
print(f"  W_FLUENCY = {{W_FLUENCY_WRONG}}")
print(f"  W_DOMAIN = {{W_DOMAIN_WRONG}}")
print(f"  W_ADAPTIVE = {{W_ADAPTIVE_WRONG}}")
print(f"  Sum of VR weights = {{W_FLUENCY_WRONG + W_DOMAIN_WRONG + W_ADAPTIVE_WRONG}} (should be 1.0!)")
""", language='python')
    # Widget: Button to demonstrate mistake 1
    if st.button("Demonstrate Mistake 1 (Bad Weights)"):
        st.session_state.mistake1_output = simulate_bad_settings_load_output()
        st.error("Demonstrated bad weight configuration leading to a ValueError.")
    # Display output if available
    if st.session_state.mistake1_output:
        st.markdown(f"**FIX**: The `model_validator` in `Settings` class catches this at startup.")
        st.markdown(f"Output simulating loading settings with incorrect weights:")
        st.code(st.session_state.mistake1_output, language='python')
        if st.session_state.settings_object:
            st.markdown(f"Current (valid) settings: W_FLUENCY={st.session_state.settings_object.W_FLUENCY}, Sum={st.session_state.settings_object.W_FLUENCY + st.session_state.settings_object.W_DOMAIN + st.session_state.settings_object.W_ADAPTIVE}")
        else:
            st.info("Current valid settings not available. Please complete 'Task 1.2: Configuration System'.")

    st.subheader("Mistake 2: Exposing secrets in logs")
    st.markdown(f"**PROBLEM**: Sensitive API keys or credentials are logged directly, creating a security vulnerability.")
    st.markdown(f"**WRONG Example**: Logging the actual API key directly.")
    st.code(f"""
dummy_api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
print(f"  Using key: {{dummy_api_key}}") # This would print the full key!
""", language='python')
    # Widget: Button to demonstrate mistake 2
    if st.button("Demonstrate Mistake 2 (Secret Exposure)"):
        st.session_state.mistake2_output = simulate_secret_str_handling_output()
        st.info("Demonstrated `SecretStr` masking sensitive values.")
    # Display output if available
    if st.session_state.mistake2_output:
        st.markdown(f"**FIX**: Use `SecretStr` which masks values.")
        st.markdown(f"Output showing `SecretStr` in action:")
        st.code(st.session_state.mistake2_output, language='python')
        st.markdown(f"To access the raw value (only when strictly necessary, e.g., passing to an API client): `settings.OPENAI_API_KEY.get_secret_value()`")

    st.subheader("Mistake 3: Missing lifespan context manager")
    st.markdown(f"**PROBLEM**: Resources (database connections, thread pools) are not properly cleaned up on application shutdown, leading to leaks.")
    st.markdown(f"**WRONG Example**: FastAPI app without a lifespan context manager.")
    st.code(f"""
app = FastAPI() # Resources leak on shutdown!
print("  FastAPI app initialized without lifespan. (Resources would leak!)")
""", language='python')
    # Widget: Button to demonstrate mistake 3
    if st.button("Demonstrate Mistake 3 (Missing Lifespan)"):
        if st.session_state.fastapi_app_object and st.session_state.settings_object:
            st.session_state.mistake3_output = asyncio.run(
                simulate_app_lifespan_output_async(st.session_state.fastapi_app_object, st.session_state.settings_object)
            )
            st.info("Demonstrated app startup/shutdown with proper lifespan management.")
        else:
            st.warning("Please complete 'Task 1.2: Configuration System' and 'Task 1.3: FastAPI Application' first.")
    # Display output if available
    if st.session_state.mistake3_output:
        st.markdown(f"**FIX**: Always use `asynccontextmanager` for `lifespan` for proper startup/shutdown.")
        st.markdown(f"Output showing proper lifespan execution:")
        st.code(st.session_state.mistake3_output, language='bash')
    
    st.markdown(f"### Explanation of Execution")
    st.markdown(f"This section actively demonstrates how implementing robust practices prevents common errors:")
    st.markdown(f"1.  **Weight Sum Validation:** When attempting to load settings with incorrect scoring weights (e.g., sum not equal to 1.0), Pydantic's `model_validator` immediately raises a `ValueError`. This 'fail-fast' mechanism prevents the AI service from starting with invalid parameters that could lead to incorrect model behavior, fulfilling the goal of preventing Knight Capital-like configuration errors.")
    st.markdown(f"2.  **Secret Handling:** By using `SecretStr` for `OPENAI_API_KEY`, the output shows that the sensitive key is masked. This is a critical security measure for the AI-Readiness Platform, preventing accidental exposure of credentials in logs, console output, or error reports, significantly reducing the risk of data breaches.")
    st.markdown(f"3.  **Lifespan Management:** The simulated startup and shutdown using the `lifespan_notebook` context manager visually confirms that explicit startup and shutdown routines are executed. This ensures that resources like database connections, caching clients, or tracing exporters are properly initialized when the AI service starts and gracefully closed when it shuts down, preventing resource leaks and ensuring application stability over its lifecycle.")
    st.markdown(f"")
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
