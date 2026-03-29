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


def test_exercises_list_json_accepts_muscle_group_filter(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock(
        return_value={
            "exercises": {
                "items": [],
                "total": 0,
                "page": 1,
                "pageSize": 20,
                "totalPages": 0,
            }
        }
    )
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "exercises",
            "list",
            "--muscle-group-id",
            "11111111-1111-1111-1111-111111111111",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True


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
    mock_execute.assert_not_awaited()


def test_exercises_assign_muscles_json_output(mocker) -> None:  # type: ignore[no-untyped-def]
    """Test assigning muscle groups to an exercise."""
    mock_execute = AsyncMock()

    # First call: list muscle groups for all name/UUID resolution
    # Second call: assign mutation
    mock_execute.side_effect = [
        {
            "muscleGroups": [
                {"id": "mg-chest", "name": "Chest"},
                {"id": "mg-triceps", "name": "Triceps"},
                {"id": "mg-shoulders", "name": "Shoulders"},
            ]
        },
        {
            "assignMuscleGroups": {
                "id": "ex1",
                "name": "Bench Press",
                "description": None,
                "equipment": "Barbell",
                "muscleGroups": [
                    {
                        "muscleGroup": {"id": "mg-chest", "name": "Chest"},
                        "role": "PRIMARY",
                    },
                    {
                        "muscleGroup": {"id": "mg-triceps", "name": "Triceps"},
                        "role": "SECONDARY",
                    },
                ],
            }
        },
    ]
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "exercises",
            "assign-muscles",
            "ex1",
            "--primary",
            "chest",
            "--secondary",
            "triceps",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["name"] == "Bench Press"
    assert len(payload["data"]["muscle_groups"]) == 2


def test_exercises_assign_muscles_dry_run(mocker) -> None:  # type: ignore[no-untyped-def]
    """Test assign-muscles with --dry-run flag."""
    mock_execute = AsyncMock()

    # First call: list muscle groups for all name resolution and display mapping
    # Second call: get exercise for dry-run display
    mock_execute.side_effect = [
        {
            "muscleGroups": [
                {"id": "mg-chest", "name": "Chest"},
                {"id": "mg-triceps", "name": "Triceps"},
            ]
        },
        {
            "exercise": {
                "id": "ex1",
                "name": "Bench Press",
                "description": None,
                "equipment": "Barbell",
                "muscleGroups": [],  # Currently no muscle groups
            }
        },
    ]
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "exercises",
            "assign-muscles",
            "ex1",
            "--primary",
            "chest",
            "--secondary",
            "triceps",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["operation"] == "assignMuscleGroups"
    # Should not have called the mutation (2 calls total)
    assert mock_execute.await_count == 2


def test_exercises_assign_muscles_invalid_name(mocker) -> None:  # type: ignore[no-untyped-def]
    """Test assign-muscles with invalid muscle group name."""
    mock_execute = AsyncMock(
        return_value={
            "muscleGroups": [
                {"id": "mg-chest", "name": "Chest"},
                {"id": "mg-back", "name": "Back"},
            ]
        }
    )
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "exercises",
            "assign-muscles",
            "ex1",
            "--primary",
            "InvalidMuscle",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output.strip())
    assert payload["success"] is False
    assert "InvalidMuscle" in payload["error"]["message"]


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
