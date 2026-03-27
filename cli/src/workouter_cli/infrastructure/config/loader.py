"""Environment configuration loading and validation."""

from dataclasses import dataclass
from os import getenv

from pydantic import ValidationError

from workouter_cli.infrastructure.config.schema import Config
from workouter_cli.utils.exit_codes import ExitCode


@dataclass(slots=True)
class ConfigError(Exception):
    """Error raised when runtime configuration is invalid."""

    message: str
    exit_code: ExitCode

    def __str__(self) -> str:
        return self.message


def load_config() -> Config:
    """Load and validate configuration from environment variables."""

    api_key = getenv("WORKOUTER_API_KEY")
    api_url = getenv("WORKOUTER_API_URL")

    if not api_key:
        raise ConfigError(
            "Missing required environment variable: WORKOUTER_API_KEY",
            ExitCode.AUTH_ERROR,
        )

    if not api_url:
        raise ConfigError(
            "Missing required environment variable: WORKOUTER_API_URL",
            ExitCode.AUTH_ERROR,
        )

    raw_timeout = getenv("WORKOUTER_CLI_TIMEOUT", "30")
    raw_log_level = getenv("WORKOUTER_CLI_LOG_LEVEL", "INFO")

    payload = {
        "api_url": api_url,
        "api_key": api_key,
        "timeout": raw_timeout,
        "log_level": raw_log_level,
    }

    try:
        return Config.model_validate(payload)
    except ValidationError as exc:
        raise ConfigError(
            f"Invalid CLI configuration: {exc.errors()[0]['msg']}",
            ExitCode.USER_ERROR,
        ) from exc
