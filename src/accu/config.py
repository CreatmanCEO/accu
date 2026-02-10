"""Application configuration management."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProviderSettings(BaseSettings):
    """AI provider configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    default_provider: str = "openrouter"
    default_model: str = "anthropic/claude-3-haiku"

    daily_budget_usd: float = Field(default=50.0, alias="AI_DAILY_BUDGET_USD")
    alert_threshold_usd: float = Field(default=10.0, alias="AI_ALERT_THRESHOLD_USD")


class GitHubSettings(BaseSettings):
    """GitHub API configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    token: str = Field(default="", alias="GITHUB_TOKEN")
    api_version: str = "2022-11-28"
    rate_limit_buffer: float = 0.8  # Use 80% of rate limit


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    url: str = Field(
        default="postgresql+asyncpg://accu:accu@localhost:5432/accu",
        alias="DATABASE_URL",
    )
    echo: bool = False


class RedisSettings(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="API_DEBUG")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="console", alias="LOG_FORMAT")

    # Nested settings
    ai: AIProviderSettings = Field(default_factory=AIProviderSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
