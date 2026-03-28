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


def _session_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "plannedSessionId": None,
        "mesocycleId": "22222222-2222-2222-2222-222222222222",
        "routineId": "33333333-3333-3333-3333-333333333333",
        "status": "COMPLETED",
        "startedAt": "2026-01-01T10:00:00Z",
        "completedAt": "2026-01-01T11:00:00Z",
        "notes": None,
        "exercises": [],
    }


def test_insight_commands_json(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "query MesocycleVolumeInsight" in query:
            calls.append("volume")
            return {
                "mesocycleVolumeInsight": {
                    "mesocycleId": "22222222-2222-2222-2222-222222222222",
                    "weeklyVolumes": [
                        {
                            "weekNumber": 1,
                            "muscleGroupId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "muscleGroupName": "Chest",
                            "setCount": 12,
                        }
                    ],
                    "totalSets": 12,
                    "muscleGroupBreakdown": [
                        {
                            "muscleGroupId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "muscleGroupName": "Chest",
                            "totalSets": 12,
                        }
                    ],
                }
            }
        if "query MesocycleIntensityInsight" in query:
            calls.append("intensity")
            return {
                "mesocycleIntensityInsight": {
                    "mesocycleId": "22222222-2222-2222-2222-222222222222",
                    "weeklyIntensities": [{"weekNumber": 1, "avgRir": 2.0}],
                    "overallAvgRir": 2.0,
                }
            }
        if "query ProgressiveOverloadInsight" in query:
            calls.append("overload")
            return {
                "progressiveOverloadInsight": {
                    "exerciseId": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                    "mesocycleId": "22222222-2222-2222-2222-222222222222",
                    "weeklyProgress": [
                        {
                            "weekNumber": 1,
                            "maxWeight": 80.0,
                            "avgReps": 10.0,
                            "avgRir": 2.0,
                        }
                    ],
                    "estimatedOneRepMaxProgression": [100.0],
                }
            }
        if "query ExerciseHistory" in query:
            calls.append("history")
            return {
                "exerciseHistory": {
                    "items": [_session_payload()],
                    "total": 1,
                    "page": 1,
                    "pageSize": 20,
                    "totalPages": 1,
                }
            }
        raise AssertionError("Unexpected GraphQL operation")

    mocker.patch(
        "workouter_cli.infrastructure.graphql.client.GraphQLClient.execute",
        new=fake_execute,
    )

    runner = CliRunner(env=_base_env())

    volume_result = runner.invoke(
        cli,
        [
            "--json",
            "insights",
            "volume",
            "--mesocycle-id",
            "22222222-2222-2222-2222-222222222222",
        ],
    )
    assert volume_result.exit_code == 0
    assert json.loads(volume_result.output.strip())["data"]["total_sets"] == 12

    intensity_result = runner.invoke(
        cli,
        [
            "--json",
            "insights",
            "intensity",
            "--mesocycle-id",
            "22222222-2222-2222-2222-222222222222",
        ],
    )
    assert intensity_result.exit_code == 0

    overload_result = runner.invoke(
        cli,
        [
            "--json",
            "insights",
            "overload",
            "--mesocycle-id",
            "22222222-2222-2222-2222-222222222222",
            "--exercise-id",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        ],
    )
    assert overload_result.exit_code == 0

    history_result = runner.invoke(
        cli,
        [
            "--json",
            "insights",
            "history",
            "--exercise-id",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        ],
    )
    assert history_result.exit_code == 0
    assert json.loads(history_result.output.strip())["data"]["items"][0]["status"] == "COMPLETED"

    assert calls == ["volume", "intensity", "overload", "history"]
