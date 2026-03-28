from __future__ import annotations

import json

from click.testing import CliRunner

from workouter_cli.main import cli


def _base_env() -> dict[str, str]:
    return {
        "WORKOUTER_API_URL": "http://localhost:8000/graphql",
        "WORKOUTER_API_KEY": "test-api-key",
        "WORKOUTER_CLI_TIMEOUT": "30",
        "WORKOUTER_CLI_LOG_LEVEL": "INFO",
    }


def test_backup_trigger_command(mocker) -> None:  # type: ignore[no-untyped-def]
    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "mutation TriggerBackup" in query:
            return {
                "triggerBackup": {
                    "success": True,
                    "filename": "backup-20260101.sql",
                    "sizeBytes": 1024,
                    "createdAt": "2026-01-01T10:00:00Z",
                }
            }
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())
    result = runner.invoke(cli, ["--json", "backup", "trigger"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["success"] is True
    assert payload["data"]["filename"] == "backup-20260101.sql"
