import os

import pytest


@pytest.fixture
def base_env() -> dict[str, str]:
    return {
        "WORKOUTER_API_URL": "http://localhost:8000/graphql",
        "WORKOUTER_API_KEY": "test-api-key",
        "WORKOUTER_CLI_TIMEOUT": "30",
        "WORKOUTER_CLI_LOG_LEVEL": "INFO",
    }


@pytest.fixture
def clean_workouter_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("WORKOUTER_"):
            monkeypatch.delenv(key, raising=False)
