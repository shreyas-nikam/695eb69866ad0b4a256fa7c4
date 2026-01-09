from typing import Literal, Optional, List, Dict, Any
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
    OPENAI_API_KEY: Optional[SecretStr] = "sk-xxxx"
    ANTHROPIC_API_KEY: Optional[SecretStr] = "anthropic-xxxx"

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
            raise ValueError(
                f"Fluency weights must sum to 1.0, got {fluency_sum}")
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
