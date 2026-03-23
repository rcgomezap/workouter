import os
import yaml
from typing import Optional
from pathlib import Path
from pydantic import ValidationError

from app.config.schema import Config


class ConfigError(Exception):
    """Base class for configuration errors."""
    pass


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load and validate configuration from a YAML file.
    
    The config path is determined by:
    1. config_path argument
    2. CONFIG_PATH environment variable
    3. Default to 'config.yaml' in the project root
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")

    path = Path(config_path)
    
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path.absolute()}")

    try:
        with open(path, "r") as f:
            raw_config = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing YAML configuration: {e}")
    except Exception as e:
        raise ConfigError(f"Unexpected error reading configuration file: {e}")

    try:
        return Config.model_validate(raw_config)
    except ValidationError as e:
        # Format Pydantic validation errors for better readability
        error_messages = []
        for error in e.errors():
            # Handle Pydantic v2 error format
            loc_parts = []
            for item in error["loc"]:
                loc_parts.append(str(item))
            loc = " -> ".join(loc_parts)
            msg = error["msg"]
            error_messages.append(f"{loc}: {msg}")
        
        raise ConfigError(
            "Configuration validation failed:\n" + "\n".join(error_messages)
        )
