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


def _bodyweight_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "weightKg": 80.5,
        "recordedAt": "2026-01-01T08:00:00Z",
        "notes": "Morning fasted",
        "createdAt": "2026-01-01T08:00:00Z",
    }


def test_bodyweight_list_log_update_delete_commands(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query ListBodyweightLogs" in query:
            calls.append("list")
            return {
                "bodyweightLogs": {
                    "items": [_bodyweight_payload()],
                    "total": 1,
                    "page": 1,
                    "pageSize": 20,
                    "totalPages": 1,
                }
            }
        if "mutation LogBodyweight" in query:
            calls.append("log")
            return {"logBodyweight": _bodyweight_payload()}
        if "mutation UpdateBodyweightLog" in query:
            calls.append("update")
            payload = _bodyweight_payload()
            payload["notes"] = "Updated"
            return {"updateBodyweightLog": payload}
        if "mutation DeleteBodyweightLog" in query:
            calls.append("delete")
            return {"deleteBodyweightLog": True}
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
            "bodyweight",
            "list",
            "--date-from",
            "2026-01-01T00:00:00",
            "--date-to",
            "2026-01-02T00:00:00",
        ],
    )
    assert list_result.exit_code == 0
    assert json.loads(list_result.output.strip())["data"]["items"][0]["weight_kg"] == 80.5

    log_result = runner.invoke(
        cli,
        ["--json", "bodyweight", "log", "--weight", "80.5", "--notes", "Morning fasted"],
    )
    assert log_result.exit_code == 0

    update_result = runner.invoke(
        cli,
        [
            "--json",
            "bodyweight",
            "update",
            "11111111-1111-1111-1111-111111111111",
            "--notes",
            "Updated",
        ],
    )
    assert update_result.exit_code == 0

    delete_result = runner.invoke(
        cli,
        [
            "--json",
            "bodyweight",
            "delete",
            "11111111-1111-1111-1111-111111111111",
            "--force",
        ],
    )
    assert delete_result.exit_code == 0
    assert json.loads(delete_result.output.strip())["data"]["deleted"] is True
    assert calls == ["list", "log", "update", "delete"]


def test_bodyweight_dry_run_and_validation(mocker) -> None:  # type: ignore[no-untyped-def]
    mock_execute = AsyncMock()
    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        mock_execute,
    )

    runner = CliRunner(env=_base_env())

    dry_run_result = runner.invoke(
        cli,
        ["--json", "bodyweight", "log", "--weight", "80.0", "--dry-run"],
    )
    assert dry_run_result.exit_code == 0
    assert json.loads(dry_run_result.output.strip())["data"]["dry_run"] is True

    validation_result = runner.invoke(
        cli,
        ["--json", "bodyweight", "update", "11111111-1111-1111-1111-111111111111"],
    )
    assert validation_result.exit_code == 1
    assert json.loads(validation_result.output.strip())["error"]["code"] == "VALIDATION_ERROR"
    mock_execute.assert_not_called()
