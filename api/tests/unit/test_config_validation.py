import pytest
import yaml
from pathlib import Path
from app.config.loader import load_config, ConfigError
from app.config.schema import Config

def test_load_example_config(tmp_path):
    # Copy example config to a temp location
    example_path = Path("config.example.yaml")
    dest_path = tmp_path / "config.yaml"
    dest_path.write_text(example_path.read_text())
    
    config = load_config(str(dest_path))
    
    assert isinstance(config, Config)
    assert config.server.port == 8000
    assert config.auth.api_key == "CHANGE-ME-TO-A-SECURE-KEY"

def test_load_config_missing_file():
    with pytest.raises(ConfigError) as excinfo:
        load_config("non_existent_file.yaml")
    assert "Configuration file not found" in str(excinfo.value)

def test_load_config_invalid_yaml(tmp_path):
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("server: {port: invalid") # Missing closing brace
    
    with pytest.raises(ConfigError) as excinfo:
        load_config(str(invalid_yaml))
    assert "Error parsing YAML configuration" in str(excinfo.value)

def test_load_config_validation_error(tmp_path):
    invalid_config = tmp_path / "invalid_val.yaml"
    # server.port should be an integer, not a string that can't be converted
    invalid_config.write_text(yaml.dump({
        "server": {"port": "not-a-number"},
        "auth": {"api_key": "test"}
    }))
    
    with pytest.raises(ConfigError) as excinfo:
        load_config(str(invalid_config))
    assert "Configuration validation failed" in str(excinfo.value)
    assert "server -> port" in str(excinfo.value)

def test_load_config_missing_required_field(tmp_path):
    invalid_config = tmp_path / "missing_field.yaml"
    # auth.api_key is required
    invalid_config.write_text(yaml.dump({
        "server": {"port": 8000}
    }))
    
    with pytest.raises(ConfigError) as excinfo:
        load_config(str(invalid_config))
    assert "auth: Field required" in str(excinfo.value)
