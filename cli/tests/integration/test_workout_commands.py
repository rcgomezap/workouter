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


def _session_payload(status: str) -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "plannedSessionId": "77777777-7777-7777-7777-777777777777",
        "mesocycleId": None,
        "routineId": "66666666-6666-6666-6666-666666666666",
        "status": status,
        "startedAt": "2026-01-01T10:00:00Z",
        "completedAt": None,
        "notes": None,
        "exercises": [],
    }


def test_workout_start_runs_calendar_create_start_in_order(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "calendarDay" in query:
            calls.append("calendarDay")
            return {
                "calendarDay": {
                    "date": "2026-01-01",
                    "plannedSession": {
                        "id": "77777777-7777-7777-7777-777777777777",
                        "routine": {
                            "id": "66666666-6666-6666-6666-666666666666",
                            "name": "Push Day",
                        },
                        "dayOfWeek": 4,
                        "date": "2026-01-01",
                        "notes": None,
                    },
                    "session": None,
                    "isCompleted": False,
                    "isRestDay": False,
                }
            }
        if "createSession" in query:
            calls.append("createSession")
            return {"createSession": _session_payload("PLANNED")}
        if "startSession" in query:
            calls.append("startSession")
            return {"startSession": _session_payload("IN_PROGRESS")}
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "workout", "start", "--date", "2026-01-01"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["status"] == "IN_PROGRESS"
    assert calls == ["calendarDay", "createSession", "startSession"]


def test_workout_start_dry_run_does_not_call_api(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock()
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "workout",
            "start",
            "--routine-id",
            "66666666-6666-6666-6666-666666666666",
            "--mesocycle-id",
            "55555555-5555-5555-5555-555555555555",
            "--notes",
            "Leg day",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["operations"][0]["operation"] == "createSession"
    assert payload["data"]["operations"][0]["input"]["routineId"] == (
        "66666666-6666-6666-6666-666666666666"
    )
    mock_execute.assert_not_called()


def test_workout_log_without_required_flags_returns_validation_error_json(
    mocker,
) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock()
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "workout", "log", "--reps", "10", "--weight", "80"])

    assert result.exit_code == 1
    payload = json.loads(result.output.strip())
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert "--set-id" in payload["error"]["message"]
    mock_execute.assert_not_called()


def test_workout_log_autodetects_single_active_session(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "sessions(" in query:
            calls.append("sessions")
            return {
                "sessions": {
                    "items": [_session_payload("IN_PROGRESS")],
                    "total": 1,
                    "page": 1,
                    "pageSize": 2,
                    "totalPages": 1,
                }
            }
        if "logSetResult" in query:
            calls.append("logSetResult")
            return {
                "logSetResult": {
                    "id": "99999999-9999-9999-9999-999999999999",
                    "setNumber": 1,
                    "setType": "WORKING",
                    "targetReps": 10,
                    "targetRir": 2,
                    "targetWeightKg": 80.0,
                    "actualReps": 10,
                    "actualRir": 1,
                    "actualWeightKg": 82.5,
                    "weightReductionPct": None,
                    "restSeconds": 120,
                    "performedAt": "2026-01-01T10:10:00Z",
                }
            }
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(
        cli,
        [
            "--json",
            "workout",
            "log",
            "--set-id",
            "99999999-9999-9999-9999-999999999999",
            "--reps",
            "10",
            "--weight",
            "82.5",
            "--rir",
            "1",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["session_id"] == "11111111-1111-1111-1111-111111111111"
    assert payload["data"]["set"]["actual_reps"] == 10
    assert calls == ["sessions", "logSetResult"]


def test_workout_log_autodetect_errors_on_multiple_active_sessions(
    mocker,
) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock(
        return_value={
            "sessions": {
                "items": [
                    _session_payload("IN_PROGRESS"),
                    {
                        **_session_payload("IN_PROGRESS"),
                        "id": "22222222-2222-2222-2222-222222222222",
                    },
                ],
                "total": 2,
                "page": 1,
                "pageSize": 2,
                "totalPages": 1,
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
            "workout",
            "log",
            "--set-id",
            "99999999-9999-9999-9999-999999999999",
            "--reps",
            "10",
            "--weight",
            "82.5",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output.strip())
    assert payload["success"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert "Multiple active sessions" in payload["error"]["message"]
    mock_execute.assert_awaited_once()


def test_workout_complete_with_notes_updates_then_completes(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "sessions(" in query:
            calls.append("sessions")
            return {
                "sessions": {
                    "items": [_session_payload("IN_PROGRESS")],
                    "total": 1,
                    "page": 1,
                    "pageSize": 2,
                    "totalPages": 1,
                }
            }
        if "updateSession" in query:
            calls.append("updateSession")
            payload = _session_payload("IN_PROGRESS")
            payload["notes"] = "Strong day"
            return {"updateSession": payload}
        if "completeSession" in query:
            calls.append("completeSession")
            payload = _session_payload("COMPLETED")
            payload["completedAt"] = "2026-01-01T11:00:00Z"
            payload["notes"] = "Strong day"
            return {"completeSession": payload}
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "workout", "complete", "--notes", "Strong day"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["status"] == "COMPLETED"
    assert payload["data"]["notes"] == "Strong day"
    assert calls == ["sessions", "updateSession", "completeSession"]
