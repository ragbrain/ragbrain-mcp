"""Configuration management for RAGBrain MCP server."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """RAGBrain MCP server settings.

    All settings can be configured via environment variables with the RAGBRAIN_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="RAGBRAIN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    url: str = Field(
        default="http://localhost:8000",
        description="URL of the RAGBrain API server",
    )

    timeout: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="HTTP request timeout in seconds",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of search results to return",
    )

    max_document_length: int = Field(
        default=100000,
        ge=1000,
        description="Maximum document length to return (characters)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = v.upper()
        if normalized not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return normalized

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
