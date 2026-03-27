import pytest

from workouter_cli.infrastructure.config.loader import ConfigError, load_config
from workouter_cli.utils.exit_codes import ExitCode


def test_load_config_valid_env_returns_config(
    monkeypatch: pytest.MonkeyPatch,
    clean_workouter_env: None,
    base_env: dict[str, str],
) -> None:
    for key, value in base_env.items():
        monkeypatch.setenv(key, value)

    config = load_config()

    assert str(config.api_url) == "http://localhost:8000/graphql"
    assert config.api_key == "test-api-key"
    assert config.timeout == 30
    assert config.log_level == "INFO"


def test_load_config_missing_api_key_raises_auth_error(
    monkeypatch: pytest.MonkeyPatch,
    clean_workouter_env: None,
) -> None:
    monkeypatch.setenv("WORKOUTER_API_URL", "http://localhost:8000/graphql")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    assert "WORKOUTER_API_KEY" in str(exc_info.value)
    assert exc_info.value.exit_code == ExitCode.AUTH_ERROR


def test_load_config_invalid_url_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
    clean_workouter_env: None,
) -> None:
    monkeypatch.setenv("WORKOUTER_API_URL", "not-a-url")
    monkeypatch.setenv("WORKOUTER_API_KEY", "test-api-key")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    assert "Invalid CLI configuration" in str(exc_info.value)
    assert exc_info.value.exit_code == ExitCode.USER_ERROR
