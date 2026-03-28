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


def _session_payload(status: str = "PLANNED") -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "plannedSessionId": None,
        "mesocycleId": "22222222-2222-2222-2222-222222222222",
        "routineId": "33333333-3333-3333-3333-333333333333",
        "status": status,
        "startedAt": "2026-01-01T10:00:00Z",
        "completedAt": None,
        "notes": "Session notes",
        "exercises": [],
    }


def _session_exercise_payload() -> dict[str, object]:
    return {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "exercise": {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "name": "Bench Press",
        },
        "order": 1,
        "supersetGroup": None,
        "restSeconds": 120,
        "notes": None,
        "sets": [],
    }


def _session_set_payload() -> dict[str, object]:
    return {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "setNumber": 1,
        "setType": "STANDARD",
        "targetReps": 10,
        "targetRir": 2,
        "targetWeightKg": 80.0,
        "actualReps": 10,
        "actualRir": 1,
        "actualWeightKg": 82.5,
        "weightReductionPct": None,
        "restSeconds": 120,
        "performedAt": "2026-01-01T10:15:00Z",
    }


def test_sessions_list_get_and_lifecycle_commands(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query ListSessions" in query:
            calls.append("list")
            return {
                "sessions": {
                    "items": [_session_payload("IN_PROGRESS")],
                    "total": 1,
                    "page": 1,
                    "pageSize": 20,
                    "totalPages": 1,
                }
            }
        if "query GetSession" in query:
            calls.append("get")
            return {"session": _session_payload("IN_PROGRESS")}
        if "mutation StartSession" in query:
            calls.append("start")
            return {"startSession": _session_payload("IN_PROGRESS")}
        if "mutation CompleteSession" in query:
            calls.append("complete")
            return {"completeSession": _session_payload("COMPLETED")}
        if "mutation DeleteSession" in query:
            calls.append("delete")
            return {"deleteSession": True}
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())

    list_result = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "list",
            "--status",
            "IN_PROGRESS",
            "--mesocycle-id",
            "22222222-2222-2222-2222-222222222222",
            "--date-from",
            "2026-01-01",
            "--date-to",
            "2026-01-31",
        ],
    )
    assert list_result.exit_code == 0
    assert json.loads(list_result.output.strip())["success"] is True

    get_result = runner.invoke(
        cli,
        ["--json", "sessions", "get", "11111111-1111-1111-1111-111111111111"],
    )
    assert get_result.exit_code == 0

    start_result = runner.invoke(
        cli,
        ["--json", "sessions", "start", "11111111-1111-1111-1111-111111111111"],
    )
    assert start_result.exit_code == 0

    complete_result = runner.invoke(
        cli,
        ["--json", "sessions", "complete", "11111111-1111-1111-1111-111111111111"],
    )
    assert complete_result.exit_code == 0

    delete_result = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "delete",
            "11111111-1111-1111-1111-111111111111",
            "--force",
        ],
    )
    assert delete_result.exit_code == 0
    assert json.loads(delete_result.output.strip())["data"]["deleted"] is True
    assert calls == ["list", "get", "start", "complete", "delete"]


def test_sessions_create_update_and_dry_run_validation(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock(return_value={"createSession": _session_payload("PLANNED")})
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())

    dry_run_create = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "create",
            "--routine-id",
            "33333333-3333-3333-3333-333333333333",
            "--dry-run",
        ],
    )
    assert dry_run_create.exit_code == 0
    assert json.loads(dry_run_create.output.strip())["data"]["dry_run"] is True
    mock_execute.assert_not_called()

    create_result = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "create",
            "--routine-id",
            "33333333-3333-3333-3333-333333333333",
        ],
    )
    assert create_result.exit_code == 0
    assert json.loads(create_result.output.strip())["data"]["status"] == "PLANNED"

    update_validation = runner.invoke(
        cli,
        ["--json", "sessions", "update", "11111111-1111-1111-1111-111111111111"],
    )
    assert update_validation.exit_code == 1
    payload = json.loads(update_validation.output.strip())
    assert payload["error"]["code"] == "VALIDATION_ERROR"


def test_sessions_nested_commands_and_remove_validations(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "mutation AddSessionExercise" in query:
            calls.append("add-exercise")
            return {"addSessionExercise": _session_payload("IN_PROGRESS")}
        if "mutation UpdateSessionExercise" in query:
            calls.append("update-exercise")
            return {"updateSessionExercise": _session_exercise_payload()}
        if "mutation RemoveSessionExercise" in query:
            calls.append("remove-exercise")
            return {"removeSessionExercise": True}
        if "mutation AddSessionSet" in query:
            calls.append("add-set")
            payload = _session_exercise_payload()
            payload["sets"] = [_session_set_payload()]
            return {"addSessionSet": payload}
        if "mutation UpdateSessionSet" in query:
            calls.append("update-set")
            return {"updateSessionSet": _session_set_payload()}
        if "mutation RemoveSessionSet" in query:
            calls.append("remove-set")
            return {"removeSessionSet": True}
        if "mutation LogSetResult" in query:
            calls.append("log-set")
            return {"logSetResult": _session_set_payload()}
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())

    add_exercise_dry_run = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "add-exercise",
            "11111111-1111-1111-1111-111111111111",
            "--exercise-id",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "--order",
            "1",
            "--dry-run",
        ],
    )
    assert add_exercise_dry_run.exit_code == 0
    assert json.loads(add_exercise_dry_run.output.strip())["data"]["dry_run"] is True

    add_exercise = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "add-exercise",
            "11111111-1111-1111-1111-111111111111",
            "--exercise-id",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "--order",
            "1",
        ],
    )
    assert add_exercise.exit_code == 0

    update_exercise_validation = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "update-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        ],
    )
    assert update_exercise_validation.exit_code == 1

    update_exercise = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "update-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "--order",
            "2",
        ],
    )
    assert update_exercise.exit_code == 0

    remove_exercise_validation = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "remove-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        ],
    )
    assert remove_exercise_validation.exit_code == 1

    remove_exercise = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "remove-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "--force",
        ],
    )
    assert remove_exercise.exit_code == 0

    add_set_dry_run = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "add-set",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "--set-number",
            "1",
            "--set-type",
            "STANDARD",
            "--dry-run",
        ],
    )
    assert add_set_dry_run.exit_code == 0

    add_set = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "add-set",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "--set-number",
            "1",
            "--set-type",
            "STANDARD",
        ],
    )
    assert add_set.exit_code == 0

    update_set_validation = runner.invoke(
        cli,
        ["--json", "sessions", "update-set", "cccccccc-cccc-cccc-cccc-cccccccccccc"],
    )
    assert update_set_validation.exit_code == 1

    update_set = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "update-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--target-reps",
            "12",
        ],
    )
    assert update_set.exit_code == 0

    remove_set_validation = runner.invoke(
        cli,
        ["--json", "sessions", "remove-set", "cccccccc-cccc-cccc-cccc-cccccccccccc"],
    )
    assert remove_set_validation.exit_code == 1

    remove_set = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "remove-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--force",
        ],
    )
    assert remove_set.exit_code == 0

    log_set = runner.invoke(
        cli,
        [
            "--json",
            "sessions",
            "log-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--reps",
            "10",
            "--weight",
            "82.5",
            "--rir",
            "1",
        ],
    )
    assert log_set.exit_code == 0
    assert json.loads(log_set.output.strip())["data"]["actual_reps"] == 10
    assert calls == [
        "add-exercise",
        "update-exercise",
        "remove-exercise",
        "add-set",
        "update-set",
        "remove-set",
        "log-set",
    ]
