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


def _mesocycle_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Hypertrophy Block",
        "description": "Upper focus",
        "startDate": "2026-01-01",
        "endDate": None,
        "status": "PLANNED",
        "weeks": [],
    }


def _paginated_mesocycles_payload() -> dict[str, object]:
    return {
        "items": [_mesocycle_payload()],
        "total": 1,
        "page": 1,
        "pageSize": 20,
        "totalPages": 1,
    }


def test_mesocycles_crud_commands_and_delete_validation(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query ListMesocycles" in query:
            calls.append("list")
            return {"mesocycles": _paginated_mesocycles_payload()}
        if "query GetMesocycle" in query:
            calls.append("get")
            return {"mesocycle": _mesocycle_payload()}
        if "mutation CreateMesocycle" in query:
            calls.append("create")
            return {"createMesocycle": _mesocycle_payload()}
        if "mutation UpdateMesocycle" in query:
            calls.append("update")
            return {"updateMesocycle": _mesocycle_payload()}
        if "mutation DeleteMesocycle" in query:
            calls.append("delete")
            return {"deleteMesocycle": True}
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
            "mesocycles",
            "list",
            "--page",
            "1",
            "--page-size",
            "20",
            "--status",
            "PLANNED",
        ],
    )
    assert list_result.exit_code == 0
    list_payload = json.loads(list_result.output.strip())
    assert list_payload["data"]["total"] == 1

    get_result = runner.invoke(
        cli,
        ["--json", "mesocycles", "get", "11111111-1111-1111-1111-111111111111"],
    )
    assert get_result.exit_code == 0

    create_dry_run = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "create",
            "--name",
            "Hypertrophy Block",
            "--start-date",
            "2026-01-01",
            "--dry-run",
        ],
    )
    assert create_dry_run.exit_code == 0
    assert json.loads(create_dry_run.output.strip())["data"]["dry_run"] is True

    create_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "create",
            "--name",
            "Hypertrophy Block",
            "--start-date",
            "2026-01-01",
        ],
    )
    assert create_result.exit_code == 0

    update_validation = runner.invoke(
        cli,
        ["--json", "mesocycles", "update", "11111111-1111-1111-1111-111111111111"],
    )
    assert update_validation.exit_code == 1

    update_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "update",
            "11111111-1111-1111-1111-111111111111",
            "--status",
            "ACTIVE",
            "--end-date",
            "2026-02-28",
        ],
    )
    assert update_result.exit_code == 0

    delete_validation = runner.invoke(
        cli,
        ["--json", "mesocycles", "delete", "11111111-1111-1111-1111-111111111111"],
    )
    assert delete_validation.exit_code == 1

    delete_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "delete",
            "11111111-1111-1111-1111-111111111111",
            "--force",
        ],
    )
    assert delete_result.exit_code == 0

    assert calls == ["list", "get", "create", "update", "delete"]
