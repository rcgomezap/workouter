"""Integration tests for muscle-groups commands."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

from click.testing import CliRunner

from workouter_cli.main import cli


def _base_env() -> dict[str, str]:
    return {
        "WORKOUTER_API_URL": "http://localhost:8000/graphql",
        "WORKOUTER_API_KEY": "test-api-key",
        "WORKOUTER_CLI_TIMEOUT": "30",
        "WORKOUTER_CLI_LOG_LEVEL": "INFO",
    }


def test_muscle_groups_list_json_output(mocker) -> None:  # type: ignore[no-untyped-def]
    """Test muscle-groups list command with JSON output."""
    mock_execute = AsyncMock(
        return_value={
            "muscleGroups": [
                {"id": "mg1", "name": "Chest"},
                {"id": "mg2", "name": "Back"},
                {"id": "mg3", "name": "Shoulders"},
            ]
        }
    )
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "muscle-groups", "list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert len(payload["data"]) == 3
    assert payload["data"][0]["name"] == "Chest"
    assert payload["data"][1]["name"] == "Back"


def test_muscle_groups_list_table_output(mocker) -> None:  # type: ignore[no-untyped-def]
    """Test muscle-groups list command with table output."""
    mock_execute = AsyncMock(
        return_value={
            "muscleGroups": [
                {"id": "mg1", "name": "Chest"},
                {"id": "mg2", "name": "Back"},
            ]
        }
    )
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["muscle-groups", "list"])

    assert result.exit_code == 0
    assert "Chest" in result.output
    assert "Back" in result.output
