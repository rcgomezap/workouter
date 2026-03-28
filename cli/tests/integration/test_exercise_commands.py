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


def test_exercises_list_json_output(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock(
        return_value={
            "exercises": {
                "items": [
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "name": "Bench Press",
                        "description": None,
                        "equipment": "Barbell",
                        "muscleGroups": [],
                    }
                ],
                "total": 1,
                "page": 1,
                "pageSize": 20,
                "totalPages": 1,
            }
        }
    )
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "exercises", "list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["items"][0]["name"] == "Bench Press"


def test_exercises_create_dry_run_does_not_call_api(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock()
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        ["--json", "exercises", "create", "--name", "Bench Press", "--dry-run"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["dry_run"] is True
    mock_execute.assert_not_called()


def test_exercises_delete_force_succeeds(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock(return_value={"deleteExercise": True})
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        ["--json", "exercises", "delete", "11111111-1111-1111-1111-111111111111", "--force"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["deleted"] is True
