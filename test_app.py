
from streamlit.testing.v1 import AppTest
import asyncio
from datetime import datetime, timedelta
import json

# Helper to configure project initialization and valid settings for tests that depend on them
def setup_project_and_settings(at: AppTest) -> AppTest:
    # Initial run to set up session state
    at.run()

    # Navigate to Project Initialization and click the button
    at.sidebar.selectbox[0].set_value("1. Project Initialization").run()
    at.button[0].click().run()
    assert at.session_state["project_initialized"] is True

    # Navigate to Configuration System
    at.sidebar.selectbox[0].set_value("2. Configuration System").run()

    # Set valid weights
    at.slider(key="sim_w_fluency").set_value(0.33).run()
    at.slider(key="sim_w_domain").set_value(0.33).run()
    at.slider(key="sim_w_adaptive").set_value(0.34).run()
    at.slider(key="sim_theta_technical").set_value(0.25).run()
    at.slider(key="sim_theta_productivity").set_value(0.25).run()
    at.slider(key="sim_theta_judgment").set_value(0.25).run()
    at.slider(key="sim_theta_velocity").set_value(0.25).run()
    at.text_input(key="OPENAI_API_KEY").set_value("sk-dummykey123").run()

    # Click Validate & Apply Settings
    at.button[0].click().run()
    assert at.session_state["settings_configured"] is True
    return at

# Helper to configure project, settings, and API core for tests that depend on them
def setup_api_core(at: AppTest) -> AppTest:
    at = setup_project_and_settings(at)
    # Navigate to API Core & Middleware
    at.sidebar.selectbox[0].set_value("3. API Core & Middleware").run()
    # Click Build API Core
    at.button[0].click().run()
    assert at.session_state["api_core_built"] is True
    return at

def test_initial_app_state_and_introduction_page():
    """Verify initial session state values and content of the Introduction page."""
    at = AppTest.from_file("app.py").run()

    # Check initial session state values
    assert at.session_state["current_page"] == "Introduction"
    assert at.session_state["project_initialized"] is False
    assert at.session_state["settings_configured"] is False
    assert at.session_state["api_core_built"] is False
    assert at.session_state["health_checks_implemented"] is False
    assert at.session_state["simulated_db_status"] == "healthy"
    assert at.session_state["simulated_redis_status"] == "healthy"
    assert at.session_state["simulated_llm_status"] == "healthy"
    assert at.session_state["openai_api_key_configured"] == ""
    # Check default values from Settings class (from source.py mock)
    assert at.session_state["current_settings"].W_FLUENCY == 0.45
    assert at.session_state["current_settings"].THETA_TECHNICAL == 0.30

    # Check Introduction page content
    assert "Introduction: The Individual AI-Readiness Platform Case Study" in at.title[0].value
    assert "Welcome to the **Individual AI-Readiness Platform** project!" in at.markdown[0].value
    assert "Tools Introduced" in at.subheader[1].value
    assert at.sidebar.selectbox[0].value == "Introduction"

def test_project_initialization():
    """Verify project initialization process, session state updates, and output messages."""
    at = AppTest.from_file("app.py").run()

    # Navigate to "1. Project Initialization"
    at.sidebar.selectbox[0].set_value("1. Project Initialization").run()
    assert at.session_state.current_page == "1. Project Initialization"

    # Verify button is initially enabled
    assert at.button[0].disabled is False

    # Click "Initialize Project" button
    at.button[0].click().run()

    # Verify success and info messages
    assert at.info[0].value == "Simulated: `individual-air-platform` directory created and `poetry init` executed."
    assert at.info[1].value == "Simulated: Core dependencies added."
    assert at.success[0].value == "Project initialization simulation complete!"
    assert at.success[1].value == "Project structure is now ready for the next steps!"

    # Verify session state updates
    assert at.session_state.project_initialized is True
    assert at.session_state.settings_configured is False # Should be reset
    assert at.session_state.api_core_built is False # Should be reset

    # Verify button is disabled after initialization
    assert at.button[0].disabled is True

def test_configuration_system_valid_settings():
    """Verify that valid configuration settings are applied successfully."""
    at = setup_project_and_settings(AppTest.from_file("app.py"))

    # Verify success message and session state
    assert at.success[0].value == "Settings validated and applied successfully!"
    assert at.session_state["settings_configured"] is True

    # Verify specific settings are updated
    assert at.session_state["current_settings"].W_FLUENCY == 0.33
    assert at.session_state["current_settings"].W_DOMAIN == 0.33
    assert at.session_state["current_settings"].W_ADAPTIVE == 0.34
    assert at.session_state["current_settings"].OPENAI_API_KEY.get_secret_value() == "sk-dummykey123"

    # Verify SecretStr masking in info message
    assert "OpenAI API Key (masked by SecretStr): **********" in at.info[0].value

def test_configuration_system_invalid_vr_weights():
    """Verify that invalid VR weight sums trigger a validation error."""
    at = AppTest.from_file("app.py").run()
    at.session_state["project_initialized"] = True  # Mock project as initialized
    at.sidebar.selectbox[0].set_value("2. Configuration System").run()

    # Set invalid VR weights (sum > 1.0)
    at.slider(key="sim_w_fluency").set_value(0.5).run()
    at.slider(key="sim_w_domain").set_value(0.4).run()
    at.slider(key="sim_w_adaptive").set_value(0.2).run() # Sum = 1.1, invalid

    # Set valid fluency weights
    at.slider(key="sim_theta_technical").set_value(0.25).run()
    at.slider(key="sim_theta_productivity").set_value(0.25).run()
    at.slider(key="sim_theta_judgment").set_value(0.25).run()
    at.slider(key="sim_theta_velocity").set_value(0.25).run()
    at.text_input(key="OPENAI_API_KEY").set_value("sk-dummykey").run()

    at.button[0].click().run()  # Click Validate & Apply Settings

    # Verify error message and session state
    assert "Configuration Validation Error: V^R weights must sum to 1.0, got 1.10" in at.error[0].value
    assert at.session_state["settings_configured"] is False

def test_configuration_system_invalid_fluency_weights():
    """Verify that invalid Fluency weight sums trigger a validation error."""
    at = AppTest.from_file("app.py").run()
    at.session_state["project_initialized"] = True  # Mock project as initialized
    at.sidebar.selectbox[0].set_value("2. Configuration System").run()

    # Set valid VR weights
    at.slider(key="sim_w_fluency").set_value(0.33).run()
    at.slider(key="sim_w_domain").set_value(0.33).run()
    at.slider(key="sim_w_adaptive").set_value(0.34).run()

    # Set invalid fluency weights (sum > 1.0)
    at.slider(key="sim_theta_technical").set_value(0.5).run()
    at.slider(key="sim_theta_productivity").set_value(0.3).run()
    at.slider(key="sim_theta_judgment").set_value(0.2).run()
    at.slider(key="sim_theta_velocity").set_value(0.1).run() # Sum = 1.1, invalid
    at.text_input(key="OPENAI_API_KEY").set_value("sk-dummykey").run()

    at.button[0].click().run()  # Click Validate & Apply Settings

    # Verify error message and session state
    assert "Configuration Validation Error: Fluency weights must sum to 1.0, got 1.10" in at.error[0].value
    assert at.session_state["settings_configured"] is False

def test_api_core_and_middleware():
    """Verify the API core build process, session state, and simulated output."""
    at = setup_project_and_settings(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("3. API Core & Middleware").run()

    # Verify button is enabled
    assert at.button[0].disabled is False

    # Click "Build API Core" button
    at.button[0].click().run()

    # Verify success message and session state
    assert at.success[0].value == "FastAPI application core simulated successfully!"
    assert at.session_state["api_core_built"] is True

    # Verify simulated code output contains expected logs
    expected_logs = [
        "Simulating `create_app_notebook()` and `lifespan_notebook` execution and its initial logs...",
        "🚀 Starting Individual AI-R Platform v4.0.0",
        "🌍 Environment: development",
        "Initializing observability tracing (simulated)...",
        "Application initialized with routers:",
        "Middleware applied: CORS, Request ID, Request Timing.",
        "Exception handlers for ValueError, HTTPException registered."
    ]
    for log in expected_logs:
        assert log in at.code[0].value

    # Verify button is disabled after build
    assert at.button[0].disabled is True

def test_health_checks_all_healthy():
    """Verify health checks when all dependencies are healthy."""
    at = setup_api_core(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("4. Health Checks").run()

    # Ensure API key is set for LLM to be healthy (done by setup_api_core)
    assert at.session_state.current_settings.OPENAI_API_KEY is not None

    # Set all selectboxes to healthy (they default to healthy, but explicit for clarity)
    at.selectbox(key="db_status_select").set_value("healthy").run()
    at.selectbox(key="redis_status_select").set_value("healthy").run()
    at.selectbox(key="llm_status_select").set_value("healthy").run()

    at.button[0].click().run()  # Click "Run Health Checks"

    assert at.session_state["health_checks_implemented"] is True

    # Basic Health Check (`/health`)
    assert at.subheader[0].value == "Basic Health Check (`/health`)"
    assert at.json[0].json["status"] == "healthy"

    # Detailed Health Check (`/health/detailed`)
    assert at.subheader[1].value == "Detailed Health Check (`/health/detailed`)"
    assert at.json[1].json["status"] == "healthy"
    assert at.json[1].json["dependencies"]["database"]["status"] == "healthy"
    assert at.json[1].json["dependencies"]["redis"]["status"] == "healthy"
    assert at.json[1].json["dependencies"]["llm"]["status"] == "healthy"
    assert at.json[1].json["dependencies"]["database"]["latency_ms"] == 10.0
    assert at.json[1].json["dependencies"]["redis"]["latency_ms"] == 5.0
    assert at.json[1].json["dependencies"]["llm"]["latency_ms"] == 20.0

    # Readiness Probe (`/health/ready`)
    assert at.subheader[2].value == "Readiness Probe (`/health/ready`)"
    assert at.success[0].value == "Status: ready"
    assert at.json[2].json["status"] == "ready"

    # Liveness Probe (`/health/live`)
    assert at.subheader[3].value == "Liveness Probe (`/health/live`)"
    assert at.success[1].value == "Status: alive (Code: 200)"
    assert at.json[3].json["status"] == "alive"

def test_health_checks_degraded_database():
    """Verify health checks when the database dependency is degraded."""
    at = setup_api_core(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("4. Health Checks").run()

    at.selectbox(key="db_status_select").set_value("degraded").run()
    at.selectbox(key="redis_status_select").set_value("healthy").run()
    at.selectbox(key="llm_status_select").set_value("healthy").run()

    at.button[0].click().run()  # Run Health Checks

    # Detailed Health Check
    assert at.json[1].json["status"] == "degraded"
    assert at.json[1].json["dependencies"]["database"]["status"] == "degraded"
    assert at.json[1].json["dependencies"]["database"]["error"] == "Simulated degraded database response"

    # Readiness Probe should be not_ready
    assert "Status: not_ready (Code: 503)" in at.error[0].value
    assert at.json[2].json["status"] == "not_ready"
    assert at.json[2].json["reason"] == "Overall status: degraded"

def test_health_checks_unhealthy_llm_api_key_not_configured():
    """Verify health checks when LLM API key is not configured."""
    at = setup_api_core(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("4. Health Checks").run()

    # Clear the API key in session state to simulate 'not_configured'
    at.session_state["current_settings"].OPENAI_API_KEY = None
    at.session_state["openai_api_key_configured"] = "" # Also clear the widget value

    at.selectbox(key="db_status_select").set_value("healthy").run()
    at.selectbox(key="redis_status_select").set_value("healthy").run()
    at.selectbox(key="llm_status_select").set_value("healthy").run() # This selection is overridden by not_configured logic

    at.button[0].click().run()  # Click "Run Health Checks"

    assert "LLM API status will reflect 'not_configured' as no API key is set." in at.info[0].value

    # Detailed Health Check
    assert at.json[1].json["status"] == "degraded" # not_configured makes overall degraded
    assert at.json[1].json["dependencies"]["llm"]["status"] == "not_configured"
    assert at.json[1].json["dependencies"]["llm"]["error"] == "OPENAI_API_KEY not set"

    # Readiness Probe should be not_ready
    assert "Status: not_ready (Code: 503)" in at.error[0].value
    assert at.json[2].json["status"] == "not_ready"
    assert at.json[2].json["reason"] == "Overall status: degraded"

def test_health_checks_unhealthy_redis():
    """Verify health checks when the Redis dependency is unhealthy."""
    at = setup_api_core(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("4. Health Checks").run()

    at.selectbox(key="db_status_select").set_value("healthy").run()
    at.selectbox(key="redis_status_select").set_value("unhealthy").run()
    at.selectbox(key="llm_status_select").set_value("healthy").run()

    at.button[0].click().run()  # Click "Run Health Checks"

    # Detailed Health Check
    assert at.json[1].json["status"] == "unhealthy"
    assert at.json[1].json["dependencies"]["redis"]["status"] == "unhealthy"
    assert at.json[1].json["dependencies"]["redis"]["error"] == "Simulated Redis connection error"

    # Readiness Probe should be not_ready
    assert "Status: not_ready (Code: 503)" in at.error[0].value
    assert at.json[2].json["status"] == "not_ready"
    assert at.json[2].json["reason"] == "Overall status: unhealthy"

def test_common_pitfalls_and_best_practices_page():
    """Verify the content and displayed information on the Common Pitfalls page."""
    at = setup_api_core(AppTest.from_file("app.py"))
    at.sidebar.selectbox[0].set_value("5. Common Pitfalls & Best Practices").run()

    assert "Avoiding Common Pitfalls: Best Practices in Action" in at.title[0].value
    assert "Mistake 1: Not validating weight sums" in at.markdown[4].value
    assert "Pydantic's `model_validator` catches this at startup." in at.markdown[6].value
    assert "Current configuration is valid. VR Sum:" in at.success[0].value
    # Verify the sums are correct from the setup_api_core
    assert "VR Sum: 1.00" in at.success[0].value
    assert "Fluency Sum: 1.00" in at.success[0].value


    assert "Mistake 2: Exposing secrets in logs" in at.markdown[8].value
    assert "Use Pydantic's `SecretStr`. It masks values upon string conversion." in at.markdown[10].value
    # Ensure the masked API key is displayed from the session state
    assert "OpenAI API Key in current settings (masked by SecretStr): **********" in at.info[0].value

    assert "Mistake 3: Missing lifespan context manager" in at.markdown[12].value
    assert "The `lifespan_notebook` is designed to handle graceful startup and shutdown, preventing resource leaks." in at.success[1].value
