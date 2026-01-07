
import pytest
import os
import shutil
from streamlit.testing.v1 import AppTest

# The Streamlit app relies on 'source.py' existing in the same directory.
# For testing purposes, we might need a dummy source.py or ensure the actual one is available.
# Assuming 'source.py' is available in the test environment for AppTest.from_file to work.

# A dummy source.py for the sake of making AppTest.from_file work if the actual one isn't present
# or if it's meant to be mocked. In a real scenario, you'd have your actual source.py.
# For this specific problem, the user stated "Do not include the source.py file code. It will be provided separately."
# So, we assume it's correctly handled by the test runner's environment.
# However, to avoid import errors during test generation, a minimal mock might be useful if not running the actual app.
# Since the problem asks for tests of the provided *Streamlit App Code*, and that app code imports `source.py`,
# a working `source.py` would be necessary for `AppTest.from_file` to succeed.
# Let's create a minimal mock for the AppTest to load the main app if a full source.py isn't present
# during the *testing code generation* phase itself, though for *running* the tests, the actual source.py is required.

# Minimal mock for source.py to allow the main app to load in AppTest context
# In a real test setup, you'd ensure the actual source.py is accessible.
# This part is a thought process for the generator, not part of the final output.
# from functools import lru_cache
# from typing import Literal, Optional
# import time
# import uuid
# from contextlib import asynccontextmanager
# import asyncio
#
# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import model_validator, SecretStr
# from fastapi import FastAPI, Request, APIRouter
#
# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env", env_file_encoding="utf-8", case_sensitive=False
#     )
#     APP_NAME: str = "Individual AI-R Platform"
#     APP_VERSION: str = "4.0.0"
#     APP_ENV: Literal["development", "staging", "production"] = "development"
#     DEBUG: bool = False
#     API_V1_PREFIX: str = "/api/v1"
#     API_V2_PREFIX: str = "/api/v2"
#     DATABASE_URL: str = "postgresql+asyncpg://air:air@localhost:5432/air_platform"
#     REDIS_URL: str = "redis://localhost:6379/0"
#     OPENAI_API_KEY: Optional[SecretStr] = None
#     ANTHROPIC_API_KEY: Optional[SecretStr] = None
#     DAILY_COST_BUDGET_USD: float = Field(default=100.0, ge=0, description="Daily budget for external API costs in USD")
#     ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.5, le=0.7, description="Weight for Alpha VR component")
#     BETA_SYNERGY_COEF: float = Field(default=0.15, ge=0.05, le=0.20, description="Coefficient for Beta synergy factor")
#     W_FLUENCY: float = Field(default=0.45, ge=0.0, le=1.0, description="Weight for fluency component")
#     W_DOMAIN: float = Field(default=0.35, ge=0.0, le=1.0, description="Weight for domain expertise component")
#     W_ADAPTIVE: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for adaptiveness component")
#     GAMMA_EXPERIENCE: float = Field(default=0.15, ge=0.10, le=0.25, description="Gamma experience factor")
#
#     @model_validator(mode='after')
#     def validate_weight_sums(self) -> 'Settings':
#         vr_sum = self.W_FLUENCY + self.W_DOMAIN + self.W_ADAPTIVE
#         if abs(vr_sum - 1.0) > 0.001:
#             raise ValueError(f"V^R weights must sum to 1.0. Got {vr_sum:.2f}")
#         return self
#
# @lru_cache
# def get_settings() -> Settings:
#     return Settings()
#
# settings = get_settings()
#
# health_router = APIRouter()
# @health_router.get("/health", summary="Health Check", tags=["Health"])
# async def health_check_endpoint():
#     return {"status": "ok", "version": settings.APP_VERSION, "name": settings.APP_NAME, "env": settings.APP_ENV}
#
# v1_router = APIRouter()
# @v1_router.get("/status", summary="Get V1 Status", tags=["Version 1"])
# async def get_v1_status():
#     return {"message": f"Welcome to {settings.APP_NAME} API v1", "version": settings.APP_VERSION}
#
# v2_router = APIRouter()
# @v2_router.get("/status", summary="Get V2 Status", tags=["Version 2"])
# async def get_v2_status():
#     return {"message": f"Welcome to {settings.APP_NAME} API v2 - Advanced Features", "version": settings.APP_VERSION}
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield
#
# def create_app() -> FastAPI:
#     app = FastAPI(lifespan=lifespan)
#     app.add_middleware(CORSMiddleware, allow_origins=["*"])
#     @app.middleware("http")
#     async def add_request_context(request: Request, call_next):
#         response = await call_next(request)
#         return response
#     app.include_router(health_router, tags=["Health"])
#     app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
#     app.include_router(v2_router, prefix=settings.API_V2_PREFIX)
#     return app
#
# from starlette.middleware.cors import CORSMiddleware
# app = create_app()

class TestQuLabApp:

    def test_00_overview_page_content(self):
        """Verify the content of the Overview page."""
        at = AppTest.from_file("app.py").run()
        assert at.title[0].value == "QuLab: Foundation & Platform Setup"
        assert at.header[0].value == "✨ Lab Preamble"
        assert "InnovateAI Solutions is developing a new AI platform" in at.markdown[0].value
        assert "Key Objectives" in at.subheader[0].value
        assert "Tools Introduced" in at.subheader[1].value
        assert "Key Concepts" in at.subheader[2].value
        assert "Prerequisites" in at.subheader[3].value
        assert "Time Estimate" in at.subheader[4].value
        assert "1.1 Objectives" in at.subheader[5].value

    def test_01_project_initialization_page(self):
        """Test navigation to Project Initialization and its simulation."""
        at = AppTest.from_file("app.py").run()

        # Navigate to "1. Project Initialization"
        at.selectbox[0].set_value("1. Project Initialization").run()
        assert at.session_state.page == "1. Project Initialization"
        assert at.header[0].value == "1. Project Initialization and Monorepo Structure with Poetry"

        # Ensure project_initialized is False initially for this test run
        assert at.session_state.project_initialized is False

        # Simulate project initialization
        # The button is visible because project_initialized is False
        assert at.button[0].label == "Simulate Project Initialization"
        at.button[0].click().run()

        # Verify success message and session state
        assert at.session_state.project_initialized is True
        assert at.success[0].value == "Project structure conceptually initialized in a temporary location!"
        assert "Project directory structure and Poetry initialization conceptually completed." in at.code[0].value

    def test_02_configuration_system_valid_weights_and_api_key(self):
        """Test valid configuration settings and API key handling."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("2. Configuration System").run()
        assert at.session_state.page == "2. Configuration System"
        assert at.header[0].value == "2. Robust Configuration with Pydantic v2"

        # Set valid weights
        at.number_input(key="input_w_fluency").set_value(0.40).run()
        at.number_input(key="input_w_domain").set_value(0.30).run()
        at.number_input(key="input_w_adaptive").set_value(0.30).run()

        # Set a simulated API key
        test_api_key = "sk-test12345"
        at.text_input(key="input_openai_key").set_value(test_api_key).run()

        # Click validate button
        at.button[0].click().run()

        # Verify success and displayed summary
        assert at.success[0].value == "Configuration validated successfully!"
        assert "✅ Configuration Loaded Successfully!" in at.markdown[2].value
        assert "VR Weights: Fluency=0.4, Domain=0.3, Adaptive=0.3" in at.markdown[2].value
        assert "Sum of VR Weights: 1.000" in at.markdown[2].value
        assert "**OPENAI_API_KEY (masked by SecretStr):** *********" in at.markdown[2].value
        assert at.session_state.config_validation_output == "success"

        # Show raw API key
        at.checkbox(key="show_raw_api_key_checkbox").check().run()
        assert "Raw API Key (revealed): `sk-test12345`" in at.markdown[2].value

    def test_03_configuration_system_invalid_weights(self):
        """Test invalid configuration (weights not summing to 1.0)."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("2. Configuration System").run()
        assert at.session_state.page == "2. Configuration System"

        # Set invalid weights (sum to 1.10)
        at.number_input(key="input_w_fluency").set_value(0.50).run()
        at.number_input(key="input_w_domain").set_value(0.40).run()
        at.number_input(key="input_w_adaptive").set_value(0.20).run() # 0.5+0.4+0.2 = 1.1

        # Click validate button
        at.button[0].click().run()

        # Verify error message
        assert "❌ Configuration Validation Failed: V^R weights must sum to 1.0. Got 1.10" in at.error[0].value
        assert "V^R weights must sum to 1.0. Got 1.10 (W_FLUENCY=0.50, W_DOMAIN=0.40, W_ADAPTIVE=0.20)" in at.error[0].value
        assert "❌ Configuration Validation Failed" in at.session_state.config_validation_output

    def test_04_configuration_system_no_api_key(self):
        """Test configuration when no API key is provided."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("2. Configuration System").run()
        assert at.session_state.page == "2. Configuration System"

        # Set valid weights
        at.number_input(key="input_w_fluency").set_value(0.33).run()
        at.number_input(key="input_w_domain").set_value(0.33).run()
        at.number_input(key="input_w_adaptive").set_value(0.34).run()

        # Clear API key
        at.text_input(key="input_openai_key").set_value("").run()

        # Click validate button
        at.button[0].click().run()

        # Verify success and that API key is marked as not set
        assert at.success[0].value == "Configuration validated successfully!"
        assert "**OPENAI_API_KEY:** Not set." in at.markdown[2].value

    def test_05_fastapi_application_core_lifespan_simulation(self):
        """Test navigation to FastAPI Application Core and lifespan simulation."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("3. FastAPI Application Core").run()
        assert at.session_state.page == "3. FastAPI Application Core"
        assert at.header[0].value == "3. Building the FastAPI Application Core with Middleware"

        # Ensure fastapi_app_configured is False initially for this test run
        assert at.session_state.fastapi_app_configured is False

        # Simulate app startup and shutdown
        at.button[0].click().run()

        # Verify success message and lifespan log
        assert at.session_state.fastapi_app_configured is True
        assert at.success[0].value == "FastAPI application is conceptually configured!"
        assert "**Lifespan Simulation Output:**" in at.markdown[1].value
        assert "- 🚀 Starting Individual AI-R Platform v4.0.0 in development environment..." in at.markdown[2].value
        assert "- ✨ Application startup complete: Database connections, cache initialized." in at.markdown[3].value
        assert "- 👋 Shutting down application..." in at.markdown[4].value
        assert "- 🛑 Application shutdown complete: Resources released." in at.markdown[5].value

    def test_06_api_versioning_page_content(self):
        """Verify the content of the API Versioning page."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("4. API Versioning").run()
        assert at.session_state.page == "4. API Versioning"
        assert at.header[0].value == "4. API Versioning for Scalability and Evolution"
        assert "URI Versioning" in at.markdown[1].value
        assert "https://api.innovateai.com/api/v1/predict" in at.code[0].value
        assert "https://api.innovateai.com/api/v2/predict" in at.code[1].value

    def test_07_production_readiness_page_content(self):
        """Verify the content of the Production Readiness page."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("5. Production Readiness").run()
        assert at.session_state.page == "5. Production Readiness"
        assert at.header[0].value == "5. Conceptualizing Containerization and CI/CD for Production Readiness"
        assert "**Containerization with Docker:**" in at.markdown[1].value
        assert "**Continuous Integration (GitHub Actions):**" in at.markdown[4].value
        assert "`Dockerfile` (in project root)" in at.code[0].value
        assert "`.github/workflows/ci.yml`" in at.code[1].value

    def test_08_troubleshooting_page_content(self):
        """Verify the content of the Troubleshooting page."""
        at = AppTest.from_file("app.py").run()
        at.selectbox[0].set_value("6. Troubleshooting").run()
        assert at.session_state.page == "6. Troubleshooting"
        assert at.header[0].value == "6. Common Mistakes & Troubleshooting"
        assert "Mistake 1: Weights don't sum to 1.0" in at.subheader[0].value
        assert "Mistake 2: Exposing secrets in logs" in at.subheader[1].value
        assert "Mistake 3: Missing lifespan context manager" in at.subheader[2].value

