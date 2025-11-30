"""Tests for configuration module."""

import os

import pytest

from ragbrain_mcp.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self) -> None:
        """Test default settings values."""
        settings = Settings()
        assert settings.url == "http://localhost:8000"
        assert settings.timeout == 60.0
        assert settings.log_level == "INFO"
        assert settings.max_results == 20
        assert settings.max_document_length == 100000

    def test_custom_settings(self) -> None:
        """Test custom settings values."""
        settings = Settings(
            url="http://example.com:9000",
            timeout=30.0,
            log_level="DEBUG",
            max_results=10,
        )
        assert settings.url == "http://example.com:9000"
        assert settings.timeout == 30.0
        assert settings.log_level == "DEBUG"
        assert settings.max_results == 10

    def test_url_validation_strips_trailing_slash(self) -> None:
        """Test that trailing slash is stripped from URL."""
        settings = Settings(url="http://localhost:8000/")
        assert settings.url == "http://localhost:8000"

    def test_url_validation_requires_http(self) -> None:
        """Test that URL must start with http:// or https://."""
        with pytest.raises(ValueError, match="URL must start with"):
            Settings(url="localhost:8000")

    def test_url_validation_accepts_https(self) -> None:
        """Test that https:// URLs are accepted."""
        settings = Settings(url="https://secure.example.com")
        assert settings.url == "https://secure.example.com"

    def test_log_level_validation(self) -> None:
        """Test that log level is validated and normalized."""
        settings = Settings(log_level="debug")
        assert settings.log_level == "DEBUG"

    def test_log_level_invalid(self) -> None:
        """Test that invalid log level raises error."""
        with pytest.raises(ValueError, match="Invalid log level"):
            Settings(log_level="VERBOSE")

    def test_timeout_bounds(self) -> None:
        """Test timeout bounds validation."""
        with pytest.raises(ValueError):
            Settings(timeout=0.5)  # Below minimum
        with pytest.raises(ValueError):
            Settings(timeout=400.0)  # Above maximum

    def test_max_results_bounds(self) -> None:
        """Test max_results bounds validation."""
        with pytest.raises(ValueError):
            Settings(max_results=0)
        with pytest.raises(ValueError):
            Settings(max_results=200)

    def test_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test settings from environment variables."""
        monkeypatch.setenv("RAGBRAIN_URL", "http://remote:8080")
        monkeypatch.setenv("RAGBRAIN_TIMEOUT", "45")
        monkeypatch.setenv("RAGBRAIN_LOG_LEVEL", "WARNING")

        settings = Settings()
        assert settings.url == "http://remote:8080"
        assert settings.timeout == 45.0
        assert settings.log_level == "WARNING"


class TestGetSettings:
    """Tests for get_settings function."""

    def test_returns_settings_instance(self) -> None:
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
