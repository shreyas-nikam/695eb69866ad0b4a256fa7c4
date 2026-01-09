
import pytest
from streamlit.testing.v1 import AppTest
import os
import asyncio
from unittest.mock import patch, MagicMock

# Assuming 'source.py' is available and its functions (like get_settings, create_app_notebook,
# health_check_func, etc.) are importable and behave as described in the Streamlit app.
# For the purpose of these tests, we will not include the content of 'source.py'
# but rely on its expected functionality as demonstrated by the 'simulate_' functions.

# Helper to run async functions for health checks within a sync test environment
def run_async(func, *args, **kwargs):
    return asyncio.run(func(*args, **kwargs))

@pytest.fixture(autouse=True)
def run_around_tests():
    # Clear session state and environment variables before each test
    # This helps ensure tests are isolated
    # AppTest.from_file already creates a fresh session state.
    # We only need to worry about global changes like os.environ.
    original_env = os.environ.copy()
    yield
    # Restore original environment variables after each test
    os.environ.clear()
    os.environ.update(original_env)

# Define common page names for easier navigation
PAGES = [
    'Introduction',
    'Task 1.1: Project Initialization',
    'Task 1.2: Configuration System',
    'Task 1.3: FastAPI Application',
    'Task 1.4: Health Check',
    'Common Mistakes & Troubleshooting'
]

def test_page_navigation():
    at = AppTest.from_file("app.py").run()

    for i, page in enumerate(PAGES):
        # Select the page from the sidebar
        at.sidebar.selectbox[0].set_value(page).run()
        # Verify the main header reflects the current page
        assert at.header[0].value == page.split(': ')[-1] if ': ' in page else page


def test_introduction_page_content():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Introduction').run()

    assert at.header[0].value == "Introduction: The Individual AI-Readiness Platform Case Study"
    assert "Welcome to the **Individual AI-Readiness Platform** project!" in at.markdown[1].value
    assert "Dependencies assumed to be installed for this interactive lab environment." in at.success[0].value


def test_task_1_1_project_initialization():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Task 1.1: Project Initialization').run()

    assert at.header[0].value == "2. Project Kick-off: Laying the Foundation for the AI-Readiness Platform"
    
    # Simulate button click
    at.button[0].click().run()

    # Assert output
    assert at.success[0].value == "Project Initialization Simulated!"
    assert "Project 'individual-air-platform' initialized with Poetry." in at.code[0].value
    assert "src/air/__init__.py" in at.code[0].value


def test_task_1_2_configuration_system():
    # Temporarily set environment variables to ensure settings are loaded correctly for SecretStr
    os.environ['OPENAI_API_KEY'] = "sk-test-key-123"
    os.environ['W_FLUENCY'] = '0.3'
    os.environ['W_DOMAIN'] = '0.3'
    os.environ['W_ADAPTIVE'] = '0.4' # Sum = 1.0

    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Task 1.2: Configuration System').run()

    assert at.header[0].value == "3. Safeguarding Configuration: Pydantic Validation in Action"
    assert "Knight Capital incident" in at.markdown[3].value

    # Simulate button click
    at.button[0].click().run()

    # Assert output
    assert at.success[0].value == "Settings loaded and validated!"
    assert "Application Name: TestApp" in at.code[0].value # Based on default mock settings.APP_NAME
    assert "Sum of VR weights: 1.0" in at.code[0].value
    assert "OpenAI API Key (masked): ****************" in at.code[0].value # SecretStr should mask


@patch('source.create_app_notebook')
@patch('source.get_settings')
def test_task_1_3_fastapi_application(mock_get_settings, mock_create_app_notebook):
    # Mock settings and FastAPI app for this test, assuming Task 1.2 has been run
    mock_settings_instance = MagicMock()
    mock_settings_instance.APP_NAME = "TestApp"
    mock_settings_instance.APP_VERSION = "0.1.0"
    mock_settings_instance.APP_ENV = "development"
    mock_settings_instance.API_V1_PREFIX = "/api/v1"
    mock_settings_instance.API_V2_PREFIX = "/api/v2"
    mock_settings_instance.DEBUG = True
    mock_settings_instance.parameter_version = "v1"
    mock_settings_instance.GUARDRAILS_ENABLED = False
    mock_settings_instance.DAILY_COST_BUDGET_USD = 100.0

    mock_get_settings.return_value = mock_settings_instance
    mock_create_app_notebook.return_value = MagicMock() # Return a dummy FastAPI app object

    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Task 1.3: FastAPI Application').run()

    assert at.header[0].value == "4. Building the API Core: Versioned Routers and Middleware"
    
    # Explicitly set session state for settings_object as it's a dependency
    at.session_state["settings_object"] = mock_settings_instance
    at.run() # Rerun to pick up session state change

    # Simulate button click
    at.button[0].click().run()

    # Assert output
    assert at.success[0].value == "FastAPI Application created and startup simulated!"
    assert "🚀 Starting TestApp v0.1.0" in at.code[0].value
    assert "App initialized with routes: " in at.markdown[3].value
    assert "- GET /api/v1/items" in at.markdown[4].value
    assert "- GET /api/v2/items" in at.markdown[5].value


@patch('source.liveness_check_func')
@patch('source.readiness_check_func')
@patch('source.detailed_health_check_func')
@patch('source.health_check_func')
@patch('source.get_settings')
def test_task_1_4_health_check(mock_get_settings, mock_health_check_func,
                               mock_detailed_health_check_func, mock_readiness_check_func,
                               mock_liveness_check_func):
    # Mock settings and app object as dependencies
    mock_settings_instance = MagicMock()
    mock_settings_instance.APP_NAME = "TestApp"
    mock_settings_instance.APP_VERSION = "0.1.0"
    mock_settings_instance.APP_ENV = "development"
    mock_get_settings.return_value = mock_settings_instance

    mock_fastapi_app_instance = MagicMock()

    # Mock health check function returns
    mock_health_check_response = MagicMock()
    mock_health_check_response.model_dump_json.return_value = '{"status": "healthy", "app_name": "TestApp"}'
    mock_health_check_func.return_value = mock_health_check_response

    mock_detailed_health_response = MagicMock()
    mock_detailed_health_response.model_dump_json.return_value = '{"status": "healthy", "dependencies": []}'
    mock_detailed_health_check_func.return_value = mock_detailed_health_response

    mock_readiness_check_func.return_value = ({"message": "Service is ready"}, 200)
    mock_liveness_check_func.return_value = ({"message": "Service is alive"}, 200)

    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Task 1.4: Health Check').run()

    assert at.header[0].value == "5. Ensuring Service Reliability: Comprehensive Health Checks"

    # Explicitly set session state for settings_object and fastapi_app_object
    at.session_state["settings_object"] = mock_settings_instance
    at.session_state["fastapi_app_object"] = mock_fastapi_app_instance
    at.run() # Rerun to pick up session state changes

    # Test Basic Health Check
    at.button[0].click().run()
    assert at.success[0].value == "Basic Health Check Completed!"
    assert '{"status": "healthy", "app_name": "TestApp"}' in at.code[0].value

    # Test Detailed Health Check
    at.button[1].click().run()
    assert at.success[1].value == "Detailed Health Check Completed!"
    assert '{"status": "healthy", "dependencies": []}' in at.code[1].value

    # Test Readiness Probe
    at.button[2].click().run()
    assert at.success[2].value == "Readiness Probe Completed: Service is Ready!"
    assert "Status Code: 200" in at.code[2].value
    assert "Content: {'message': 'Service is ready'}" in at.code[2].value # Check for dictionary string representation

    # Test Liveness Probe
    at.button[3].click().run()
    assert at.success[3].value == "Liveness Probe Completed: Service is Alive!"
    assert "Status Code: 200" in at.code[3].value
    assert "Content: {'message': 'Service is alive'}" in at.code[3].value


@patch('source.get_settings')
def test_common_mistakes_and_troubleshooting(mock_get_settings):
    # Mock settings for valid state, if needed by the app's internal logic
    mock_settings_instance = MagicMock()
    mock_settings_instance.APP_NAME = "TestApp"
    mock_settings_instance.W_FLUENCY = 0.3
    mock_settings_instance.W_DOMAIN = 0.3
    mock_settings_instance.W_ADAPTIVE = 0.4 # Sum is 1.0
    mock_settings_instance.OPENAI_API_KEY = "dummy-secret" # Not SecretStr for mock, just a string
    mock_get_settings.return_value = mock_settings_instance

    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value('Common Mistakes & Troubleshooting').run()

    assert at.header[0].value == "6. Avoiding Common Pitfalls: Best Practices in Action"

    # Mistake 1: Not validating weight sums
    # simulate_bad_settings_load_output internally sets and cleans env vars
    at.button[0].click().run()
    assert at.error[0].value == "Demonstrated bad weight configuration leading to a ValueError."
    assert "Successfully caught validation error: 1 validation error for Settings" in at.code[1].value # Citing the Pydantic error

    # Mistake 2: Exposing secrets in logs
    # simulate_secret_str_handling_output internally sets and cleans env vars
    at.button[1].click().run()
    assert at.info[0].value == "Demonstrated `SecretStr` masking sensitive values."
    assert "OpenAI API Key (using SecretStr): ****************" in at.code[2].value

    # Mistake 3: Missing lifespan context manager
    # Need to set settings_object and fastapi_app_object in session_state for this to run
    at.session_state["settings_object"] = mock_settings_instance
    at.session_state["fastapi_app_object"] = MagicMock()
    at.run() # Rerun to pick up session state changes

    at.button[2].click().run()
    assert at.info[1].value == "Demonstrated app startup/shutdown with proper lifespan management."
    assert "Application started up (resources initialized)." in at.code[3].value
    assert "👋 Shutting down (resources cleaned up)." in at.code[3].value
