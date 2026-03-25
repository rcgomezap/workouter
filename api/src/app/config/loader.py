import os
import yaml
from typing import Any, Optional
from pathlib import Path
from pydantic import ValidationError

from app.config.schema import Config


class ConfigError(Exception):
    """Base class for configuration errors."""

    pass


def _merge_env_overrides(config_dict: dict[str, Any]) -> None:
    """
    Apply environment variable overrides to the config dictionary.
    Supports nested keys using double underscores (e.g., WT_SERVER__PORT -> server.port).
    """
    prefix = "WT_"
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue

        # WT_SERVER__PORT -> ["SERVER", "PORT"]
        parts = key[len(prefix) :].lower().split("__")

        current = config_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Handle type conversion for numbers and booleans
        val = value
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        else:
            try:
                if "." in val:
                    val = float(val)
                else:
                    val = int(val)
            except ValueError:
                pass

        current[parts[-1]] = val


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load and validate configuration from a YAML file with environment overrides.

    The config path is determined by:
    1. config_path argument
    2. CONFIG_PATH environment variable
    3. Default to 'config.yaml' in the project root
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")

    path = Path(config_path)

    # If using default 'config.yaml' and not found, try looking one directory up
    if config_path == "config.yaml" and not path.exists():
        alt_path = Path("..") / "config.yaml"
        if alt_path.exists():
            path = alt_path

    raw_config = {}
    if path.exists():
        try:
            with open(path, "r") as f:
                raw_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML configuration: {e}")
        except Exception as e:
            raise ConfigError(f"Unexpected error reading configuration file: {e}")

    # Apply environment overrides
    _merge_env_overrides(raw_config)

    if not raw_config and not path.exists():
        raise ConfigError(
            f"Configuration file not found and no environment overrides provided: {path.absolute()}"
        )

    try:
        return Config.model_validate(raw_config)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            loc_parts = [str(item) for item in error["loc"]]
            loc = " -> ".join(loc_parts)
            msg = error["msg"]
            error_messages.append(f"{loc}: {msg}")

        raise ConfigError("Configuration validation failed:\n" + "\n".join(error_messages))
