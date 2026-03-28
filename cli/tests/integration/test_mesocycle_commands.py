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
        "weeks": [
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "weekNumber": 1,
                "weekType": "TRAINING",
                "startDate": "2026-01-01",
                "endDate": "2026-01-07",
                "plannedSessions": [
                    {
                        "id": "33333333-3333-3333-3333-333333333333",
                        "routine": {
                            "id": "44444444-4444-4444-4444-444444444444",
                            "name": "Push A",
                        },
                        "dayOfWeek": 1,
                        "date": "2026-01-01",
                        "notes": "Heavy compounds",
                    }
                ],
            }
        ],
    }


def _paginated_mesocycles_payload() -> dict[str, object]:
    return {
        "items": [_mesocycle_payload()],
        "total": 1,
        "page": 1,
        "pageSize": 20,
        "totalPages": 1,
    }


def _week_payload() -> dict[str, object]:
    return {
        "id": "22222222-2222-2222-2222-222222222222",
        "weekNumber": 1,
        "weekType": "TRAINING",
        "startDate": "2026-01-01",
        "endDate": "2026-01-07",
        "plannedSessions": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "routine": {
                    "id": "44444444-4444-4444-4444-444444444444",
                    "name": "Push A",
                },
                "dayOfWeek": 1,
                "date": "2026-01-01",
                "notes": "Heavy compounds",
            }
        ],
    }


def _planned_session_payload() -> dict[str, object]:
    return {
        "id": "33333333-3333-3333-3333-333333333333",
        "routine": {
            "id": "44444444-4444-4444-4444-444444444444",
            "name": "Push A",
        },
        "dayOfWeek": 1,
        "date": "2026-01-01",
        "notes": "Heavy compounds",
    }


def test_mesocycles_crud_and_planning_commands(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query ListMesocycles" in query:
            calls.append("list")
            return {"mesocycles": _paginated_mesocycles_payload()}
        if "query GetMesocycle" in query:
            calls.append("get")
            return {"mesocycle": _mesocycle_payload()}
        if "mutation AddMesocycleWeek" in query:
            calls.append("add-week")
            return {"addMesocycleWeek": _week_payload()}
        if "mutation UpdateMesocycleWeek" in query:
            calls.append("update-week")
            return {"updateMesocycleWeek": _week_payload()}
        if "mutation RemoveMesocycleWeek" in query:
            calls.append("remove-week")
            return {"removeMesocycleWeek": True}
        if "mutation AddPlannedSession" in query:
            calls.append("add-session")
            return {"addPlannedSession": _planned_session_payload()}
        if "mutation UpdatePlannedSession" in query:
            calls.append("update-session")
            return {"updatePlannedSession": _planned_session_payload()}
        if "mutation RemovePlannedSession" in query:
            calls.append("remove-session")
            return {"removePlannedSession": True}
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

    add_week_dry_run = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "add-week",
            "11111111-1111-1111-1111-111111111111",
            "--week-number",
            "1",
            "--week-type",
            "TRAINING",
            "--start-date",
            "2026-01-01",
            "--end-date",
            "2026-01-07",
            "--dry-run",
        ],
    )
    assert add_week_dry_run.exit_code == 0
    assert json.loads(add_week_dry_run.output.strip())["data"]["dry_run"] is True

    add_week_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "add-week",
            "11111111-1111-1111-1111-111111111111",
            "--week-number",
            "1",
            "--week-type",
            "TRAINING",
            "--start-date",
            "2026-01-01",
            "--end-date",
            "2026-01-07",
        ],
    )
    assert add_week_result.exit_code == 0

    add_week_date_validation = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "add-week",
            "11111111-1111-1111-1111-111111111111",
            "--week-number",
            "1",
            "--week-type",
            "TRAINING",
            "--start-date",
            "2026-01-07",
            "--end-date",
            "2026-01-01",
        ],
    )
    assert add_week_date_validation.exit_code == 1

    update_week_validation = runner.invoke(
        cli,
        ["--json", "mesocycles", "update-week", "22222222-2222-2222-2222-222222222222"],
    )
    assert update_week_validation.exit_code == 1

    update_week_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "update-week",
            "22222222-2222-2222-2222-222222222222",
            "--week-type",
            "DELOAD",
        ],
    )
    assert update_week_result.exit_code == 0

    remove_week_validation = runner.invoke(
        cli,
        ["--json", "mesocycles", "remove-week", "22222222-2222-2222-2222-222222222222"],
    )
    assert remove_week_validation.exit_code == 1

    remove_week_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "remove-week",
            "22222222-2222-2222-2222-222222222222",
            "--force",
        ],
    )
    assert remove_week_result.exit_code == 0

    add_session_dry_run = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "add-session",
            "22222222-2222-2222-2222-222222222222",
            "--routine-id",
            "44444444-4444-4444-4444-444444444444",
            "--day-of-week",
            "1",
            "--date",
            "2026-01-01",
            "--dry-run",
        ],
    )
    assert add_session_dry_run.exit_code == 0
    assert json.loads(add_session_dry_run.output.strip())["data"]["dry_run"] is True

    add_session_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "add-session",
            "22222222-2222-2222-2222-222222222222",
            "--routine-id",
            "44444444-4444-4444-4444-444444444444",
            "--day-of-week",
            "1",
            "--date",
            "2026-01-01",
        ],
    )
    assert add_session_result.exit_code == 0

    update_session_validation = runner.invoke(
        cli,
        ["--json", "mesocycles", "update-session", "33333333-3333-3333-3333-333333333333"],
    )
    assert update_session_validation.exit_code == 1

    update_session_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "update-session",
            "33333333-3333-3333-3333-333333333333",
            "--notes",
            "Updated note",
        ],
    )
    assert update_session_result.exit_code == 0

    remove_session_validation = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "remove-session",
            "33333333-3333-3333-3333-333333333333",
        ],
    )
    assert remove_session_validation.exit_code == 1

    remove_session_result = runner.invoke(
        cli,
        [
            "--json",
            "mesocycles",
            "remove-session",
            "33333333-3333-3333-3333-333333333333",
            "--force",
        ],
    )
    assert remove_session_result.exit_code == 0

    assert calls == [
        "list",
        "get",
        "create",
        "update",
        "delete",
        "add-week",
        "update-week",
        "remove-week",
        "add-session",
        "update-session",
        "remove-session",
    ]
