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


def _calendar_day_payload() -> dict[str, object]:
    return {
        "date": "2026-01-01",
        "plannedSession": {
            "id": "11111111-1111-1111-1111-111111111111",
            "routine": {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "Push A",
            },
            "dayOfWeek": 4,
            "date": "2026-01-01",
            "notes": None,
        },
        "session": None,
        "isCompleted": False,
        "isRestDay": False,
    }


def test_calendar_day_and_range_commands(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query CalendarDay" in query:
            calls.append("day")
            return {"calendarDay": _calendar_day_payload()}
        if "query CalendarRange" in query:
            calls.append("range")
            return {"calendarRange": [_calendar_day_payload()]}
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())

    day_result = runner.invoke(
        cli,
        ["--json", "calendar", "day", "--date", "2026-01-01"],
    )
    assert day_result.exit_code == 0
    assert json.loads(day_result.output.strip())["data"]["date"] == "2026-01-01"

    range_result = runner.invoke(
        cli,
        [
            "--json",
            "calendar",
            "range",
            "--start-date",
            "2026-01-01",
            "--end-date",
            "2026-01-07",
        ],
    )
    assert range_result.exit_code == 0
    assert json.loads(range_result.output.strip())["data"][0]["date"] == "2026-01-01"

    assert calls == ["day", "range"]
