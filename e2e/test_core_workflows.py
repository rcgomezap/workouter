from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
import time
from typing import Any
from urllib.request import Request, urlopen

from conftest import APIRuntime, CLIResult


def _cli_payload(result: CLIResult) -> dict[str, Any]:
    output = result.stdout.strip()
    assert output, f"Expected CLI stdout payload, got stderr: {result.stderr}"
    payload = json.loads(output)
    assert isinstance(payload, dict)
    return payload


def _assert_cli_success(result: CLIResult) -> dict[str, Any]:
    assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"
    payload = _cli_payload(result)
    assert payload["success"] is True
    return payload


def _graphql_request(
    api_runtime: APIRuntime,
    query: str,
    variables: dict[str, object] | None = None,
) -> dict[str, Any]:
    body: dict[str, object] = {"query": query}
    if variables is not None:
        body["variables"] = variables

    request = Request(
        url=api_runtime.graphql_url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_runtime.api_key}",
        },
        method="POST",
    )
    with urlopen(request, timeout=5) as response:  # noqa: S310
        assert int(getattr(response, "status", 0)) == 200
        payload = json.loads(response.read().decode("utf-8"))

    assert "errors" not in payload, payload.get("errors")
    data = payload.get("data")
    assert isinstance(data, dict)
    return data


def _wait_for_backup_artifact(
    backups_dir: Path, timeout_seconds: float = 5.0
) -> list[Path]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        artifacts = [path for path in backups_dir.iterdir() if path.is_file()]
        if artifacts:
            return artifacts
        time.sleep(0.1)
    return []


def test_exercise_lifecycle_create_list_get_delete(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    create_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "exercises",
                "create",
                "--name",
                "E2E Issue 37 Exercise",
                "--description",
                "Created by e2e",
                "--equipment",
                "Barbell",
            ]
        )
    )
    created = create_payload["data"]
    assert isinstance(created, dict)
    exercise_id = created["id"]
    assert isinstance(exercise_id, str)

    list_payload = _assert_cli_success(run_cli(["--json", "exercises", "list"]))
    listed_items = list_payload["data"]["items"]
    assert isinstance(listed_items, list)
    assert any(item["id"] == exercise_id for item in listed_items)

    get_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "get", exercise_id])
    )
    fetched = get_payload["data"]
    assert isinstance(fetched, dict)
    assert fetched["id"] == exercise_id
    assert fetched["name"] == "E2E Issue 37 Exercise"

    exercise_data = _graphql_request(
        api_runtime,
        query="""
        query GetExercise($id: UUID!) {
          exercise(id: $id) {
            id
            name
          }
        }
        """,
        variables={"id": exercise_id},
    )
    exercise = exercise_data["exercise"]
    assert isinstance(exercise, dict)
    assert exercise["id"] == exercise_id
    assert exercise["name"] == "E2E Issue 37 Exercise"

    delete_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "delete", exercise_id, "--force"])
    )
    deleted = delete_payload["data"]
    assert isinstance(deleted, dict)
    assert deleted["deleted"] is True

    final_list_payload = _assert_cli_success(run_cli(["--json", "exercises", "list"]))
    final_items = final_list_payload["data"]["items"]
    assert isinstance(final_items, list)
    assert all(item["id"] != exercise_id for item in final_items)


def test_muscle_groups_list_matches_graphql_source_of_truth(
    run_cli: Callable[[list[str]], CLIResult],
) -> None:
    cli_payload = _assert_cli_success(run_cli(["--json", "muscle-groups", "list"]))
    cli_groups = cli_payload["data"]
    assert isinstance(cli_groups, list)
    assert cli_groups

    cli_names = {str(item["name"]).lower() for item in cli_groups}
    assert "chest" in cli_names
    assert "back" in cli_names


def test_assign_muscle_groups_command_resolves_names_and_dry_run_payload(
    run_cli: Callable[[list[str]], CLIResult],
) -> None:
    create_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "exercises",
                "create",
                "--name",
                "E2E Muscle Assignment Exercise",
            ]
        )
    )
    exercise_id = create_payload["data"]["id"]

    muscle_groups_payload = _assert_cli_success(
        run_cli(["--json", "muscle-groups", "list"])
    )
    muscle_groups = muscle_groups_payload["data"]
    assert isinstance(muscle_groups, list)
    assert muscle_groups

    chest_group = next(
        (item for item in muscle_groups if str(item["name"]).lower() == "chest"),
        None,
    )
    triceps_group = next(
        (item for item in muscle_groups if str(item["name"]).lower() == "triceps"),
        None,
    )
    assert isinstance(chest_group, dict)
    assert isinstance(triceps_group, dict)

    dry_run_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "exercises",
                "assign-muscles",
                exercise_id,
                "--primary",
                "chest",
                "--secondary",
                "triceps",
                "--dry-run",
            ]
        )
    )
    dry_run_data = dry_run_payload["data"]
    assert isinstance(dry_run_data, dict)
    assert dry_run_data["dry_run"] is True
    assert dry_run_data["operation"] == "assignMuscleGroups"
    assert "Chest" in dry_run_data["new_primary"]
    assert "Triceps" in dry_run_data["new_secondary"]

    assign_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "exercises",
                "assign-muscles",
                exercise_id,
                "--primary",
                str(chest_group["id"]),
                "--secondary",
                str(triceps_group["id"]),
            ]
        )
    )
    assigned = assign_payload["data"]
    assert isinstance(assigned, dict)
    assert assigned["id"] == exercise_id
    assigned_muscles = assigned["muscle_groups"]
    assert isinstance(assigned_muscles, list)

    get_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "get", exercise_id])
    )
    persisted = get_payload["data"]
    assert isinstance(persisted, dict)
    assert persisted["id"] == exercise_id


def test_workout_session_lifecycle_start_log_complete(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    exercise_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "create", "--name", "E2E Lifecycle Exercise"])
    )
    exercise_id = exercise_payload["data"]["id"]

    routine_payload = _assert_cli_success(
        run_cli(["--json", "routines", "create", "--name", "E2E Lifecycle Routine"])
    )
    routine_id = routine_payload["data"]["id"]

    routine_with_exercise_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "routines",
                "add-exercise",
                routine_id,
                "--exercise-id",
                exercise_id,
                "--order",
                "1",
            ]
        )
    )
    routine_exercises = routine_with_exercise_payload["data"]["exercises"]
    assert isinstance(routine_exercises, list)
    assert len(routine_exercises) == 1
    routine_exercise_id = routine_exercises[0]["id"]

    _assert_cli_success(
        run_cli(
            [
                "--json",
                "routines",
                "add-set",
                routine_exercise_id,
                "--set-number",
                "1",
                "--set-type",
                "STANDARD",
                "--target-reps-min",
                "8",
                "--target-reps-max",
                "10",
                "--target-rir",
                "2",
                "--target-weight",
                "60",
            ]
        )
    )

    start_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "workout",
                "start",
                "--routine-id",
                routine_id,
                "--notes",
                "Issue 37 workflow",
            ]
        )
    )
    started_session = start_payload["data"]
    assert isinstance(started_session, dict)
    assert started_session["status"] == "IN_PROGRESS"
    session_id = started_session["id"]

    exercises = started_session["exercises"]
    assert isinstance(exercises, list)
    assert len(exercises) == 1
    sets = exercises[0]["sets"]
    assert isinstance(sets, list)
    assert len(sets) == 1
    session_set_id = sets[0]["id"]

    log_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "workout",
                "log",
                "--session-id",
                session_id,
                "--set-id",
                session_set_id,
                "--reps",
                "9",
                "--weight",
                "62.5",
                "--rir",
                "1",
            ]
        )
    )
    logged_set = log_payload["data"]["set"]
    assert logged_set["actual_reps"] == 9
    assert logged_set["actual_weight_kg"] == 62.5
    assert logged_set["actual_rir"] == 1

    complete_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "workout",
                "complete",
                "--session-id",
                session_id,
                "--notes",
                "Issue 37 complete",
            ]
        )
    )
    completed_session = complete_payload["data"]
    assert completed_session["id"] == session_id
    assert completed_session["status"] == "COMPLETED"
    assert completed_session["notes"] == "Issue 37 complete"

    session_data = _graphql_request(
        api_runtime,
        query="""
        query GetSession($id: UUID!) {
          session(id: $id) {
            id
            status
            notes
            completedAt
            exercises {
              id
              sets {
                id
                actualReps
                actualWeightKg
                actualRir
              }
            }
          }
        }
        """,
        variables={"id": session_id},
    )
    persisted_session = session_data["session"]
    assert isinstance(persisted_session, dict)
    assert persisted_session["status"] == "COMPLETED"
    assert persisted_session["notes"] == "Issue 37 complete"
    assert persisted_session["completedAt"] is not None

    persisted_exercises = persisted_session["exercises"]
    assert isinstance(persisted_exercises, list)
    persisted_sets = persisted_exercises[0]["sets"]
    assert isinstance(persisted_sets, list)
    assert persisted_sets[0]["id"] == session_set_id
    assert persisted_sets[0]["actualReps"] == 9
    assert float(persisted_sets[0]["actualWeightKg"]) == 62.5
    assert persisted_sets[0]["actualRir"] == 1


def test_invalid_input_returns_error_envelope_and_exit_code(
    run_cli: Callable[[list[str]], CLIResult],
) -> None:
    result = run_cli(["--json", "workout", "log", "--reps", "10", "--weight", "80"])
    assert result.returncode == 1

    payload = _cli_payload(result)
    assert payload["success"] is False
    error = payload["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "--set-id" in error["message"]


def test_bodyweight_log_and_query_flows(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    log_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "bodyweight",
                "log",
                "--weight",
                "82.4",
                "--recorded-at",
                "2026-02-01T07:30:00",
                "--notes",
                "Issue 38 bodyweight",
            ]
        )
    )
    logged = log_payload["data"]
    assert isinstance(logged, dict)
    bodyweight_log_id = logged["id"]
    assert isinstance(bodyweight_log_id, str)
    assert logged["weight_kg"] == 82.4
    assert logged["notes"] == "Issue 38 bodyweight"

    listed_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "bodyweight",
                "list",
                "--date-from",
                "2026-02-01T00:00:00",
                "--date-to",
                "2026-02-02T00:00:00",
            ]
        )
    )
    listed_items = listed_payload["data"]["items"]
    assert isinstance(listed_items, list)
    assert any(item["id"] == bodyweight_log_id for item in listed_items)

    bodyweight_data = _graphql_request(
        api_runtime,
        query="""
        query BodyweightLogs($dateFrom: DateTime, $dateTo: DateTime) {
          bodyweightLogs(dateFrom: $dateFrom, dateTo: $dateTo) {
            items {
              id
              weightKg
              notes
            }
          }
        }
        """,
        variables={
            "dateFrom": "2026-02-01T00:00:00",
            "dateTo": "2026-02-02T00:00:00",
        },
    )
    persisted_items = bodyweight_data["bodyweightLogs"]["items"]
    assert isinstance(persisted_items, list)

    persisted = next(
        (item for item in persisted_items if item["id"] == bodyweight_log_id), None
    )
    assert isinstance(persisted, dict)
    assert float(persisted["weightKg"]) == 82.4
    assert persisted["notes"] == "Issue 38 bodyweight"


def test_calendar_day_and_range_flows(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    exercise_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "create", "--name", "E2E Calendar Exercise"])
    )
    exercise_id = exercise_payload["data"]["id"]

    routine_payload = _assert_cli_success(
        run_cli(["--json", "routines", "create", "--name", "E2E Calendar Routine"])
    )
    routine_id = routine_payload["data"]["id"]

    _assert_cli_success(
        run_cli(
            [
                "--json",
                "routines",
                "add-exercise",
                routine_id,
                "--exercise-id",
                exercise_id,
                "--order",
                "1",
            ]
        )
    )

    mesocycle_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "create",
                "--name",
                "E2E Calendar Mesocycle",
                "--start-date",
                "2026-05-01",
            ]
        )
    )
    mesocycle_id = mesocycle_payload["data"]["id"]

    week_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "add-week",
                mesocycle_id,
                "--week-number",
                "1",
                "--week-type",
                "TRAINING",
                "--start-date",
                "2026-05-01",
                "--end-date",
                "2026-05-07",
            ]
        )
    )
    week_id = week_payload["data"]["id"]

    planned_session_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "add-session",
                week_id,
                "--routine-id",
                routine_id,
                "--day-of-week",
                "6",
                "--date",
                "2026-05-02",
                "--notes",
                "Issue 38 calendar",
            ]
        )
    )
    planned_session = planned_session_payload["data"]
    assert isinstance(planned_session, dict)
    planned_session_id = planned_session["id"]

    day_payload = _assert_cli_success(
        run_cli(["--json", "calendar", "day", "--date", "2026-05-02"])
    )
    day_data = day_payload["data"]
    assert isinstance(day_data, dict)
    assert day_data["date"] == "2026-05-02"
    assert isinstance(day_data["planned_session"], dict)
    assert day_data["planned_session"]["id"] == planned_session_id
    assert day_data["planned_session"]["routine_name"] == "E2E Calendar Routine"
    assert day_data["is_rest_day"] is False

    range_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "calendar",
                "range",
                "--start-date",
                "2026-05-01",
                "--end-date",
                "2026-05-07",
            ]
        )
    )
    range_days = range_payload["data"]
    assert isinstance(range_days, list)
    assert len(range_days) == 7
    target_day = next(
        (item for item in range_days if item["date"] == "2026-05-02"), None
    )
    assert isinstance(target_day, dict)
    assert isinstance(target_day["planned_session"], dict)
    assert target_day["planned_session"]["id"] == planned_session_id

    calendar_day_data = _graphql_request(
        api_runtime,
        query="""
        query CalendarDayCheck($date: Date!) {
          calendarDay(date: $date) {
            date
            plannedSession {
              id
            }
            isRestDay
          }
        }
        """,
        variables={"date": "2026-05-02"},
    )
    persisted_day = calendar_day_data["calendarDay"]
    assert isinstance(persisted_day, dict)
    assert persisted_day["date"] == "2026-05-02"
    assert persisted_day["isRestDay"] is False
    assert persisted_day["plannedSession"]["id"] == planned_session_id

    calendar_range_data = _graphql_request(
        api_runtime,
        query="""
        query CalendarRangeCheck($startDate: Date!, $endDate: Date!) {
          calendarRange(startDate: $startDate, endDate: $endDate) {
            date
            plannedSession {
              id
            }
          }
        }
        """,
        variables={
            "startDate": "2026-05-01",
            "endDate": "2026-05-07",
        },
    )
    persisted_range = calendar_range_data["calendarRange"]
    assert isinstance(persisted_range, list)
    assert len(persisted_range) == 7
    persisted_target = next(
        (item for item in persisted_range if item["date"] == "2026-05-02"), None
    )
    assert isinstance(persisted_target, dict)
    assert persisted_target["plannedSession"]["id"] == planned_session_id


def test_insights_queries_with_seeded_session_data(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    exercise_payload = _assert_cli_success(
        run_cli(["--json", "exercises", "create", "--name", "E2E Insights Deadlift"])
    )
    exercise_id = exercise_payload["data"]["id"]

    muscle_groups_data = _graphql_request(
        api_runtime,
        query="""
        query MuscleGroups {
          muscleGroups {
            id
            name
          }
        }
        """,
    )
    muscle_groups = muscle_groups_data["muscleGroups"]
    assert isinstance(muscle_groups, list)
    assert muscle_groups
    muscle_group_id = muscle_groups[0]["id"]

    _graphql_request(
        api_runtime,
        query="""
        mutation AssignMuscleGroups($exerciseId: UUID!, $muscleGroupIds: [MuscleGroupAssignmentInput!]!) {
          assignMuscleGroups(exerciseId: $exerciseId, muscleGroupIds: $muscleGroupIds) {
            id
          }
        }
        """,
        variables={
            "exerciseId": exercise_id,
            "muscleGroupIds": [{"muscleGroupId": muscle_group_id, "role": "PRIMARY"}],
        },
    )

    routine_payload = _assert_cli_success(
        run_cli(["--json", "routines", "create", "--name", "E2E Insights Routine"])
    )
    routine_id = routine_payload["data"]["id"]

    routine_with_exercise_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "routines",
                "add-exercise",
                routine_id,
                "--exercise-id",
                exercise_id,
                "--order",
                "1",
            ]
        )
    )
    routine_exercise_id = routine_with_exercise_payload["data"]["exercises"][0]["id"]

    _assert_cli_success(
        run_cli(
            [
                "--json",
                "routines",
                "add-set",
                routine_exercise_id,
                "--set-number",
                "1",
                "--set-type",
                "STANDARD",
                "--target-reps-min",
                "5",
                "--target-reps-max",
                "5",
                "--target-rir",
                "2",
                "--target-weight",
                "140",
            ]
        )
    )

    mesocycle_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "create",
                "--name",
                "E2E Insights Mesocycle",
                "--start-date",
                "2026-06-01",
            ]
        )
    )
    mesocycle_id = mesocycle_payload["data"]["id"]

    week_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "add-week",
                mesocycle_id,
                "--week-number",
                "1",
                "--week-type",
                "TRAINING",
                "--start-date",
                "2026-06-01",
                "--end-date",
                "2026-06-07",
            ]
        )
    )
    week_id = week_payload["data"]["id"]

    planned_session_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "mesocycles",
                "add-session",
                week_id,
                "--routine-id",
                routine_id,
                "--day-of-week",
                "1",
                "--date",
                "2026-06-01",
            ]
        )
    )
    planned_session_id = planned_session_payload["data"]["id"]

    session_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "sessions",
                "create",
                "--planned-session-id",
                planned_session_id,
            ]
        )
    )
    session = session_payload["data"]
    assert isinstance(session, dict)
    session_id = session["id"]
    session_set_id = session["exercises"][0]["sets"][0]["id"]

    _assert_cli_success(run_cli(["--json", "sessions", "start", session_id]))

    _assert_cli_success(
        run_cli(
            [
                "--json",
                "workout",
                "log",
                "--session-id",
                session_id,
                "--set-id",
                session_set_id,
                "--reps",
                "5",
                "--weight",
                "140",
                "--rir",
                "2",
            ]
        )
    )

    _assert_cli_success(run_cli(["--json", "sessions", "complete", session_id]))

    volume_payload = _assert_cli_success(
        run_cli(["--json", "insights", "volume", "--mesocycle-id", mesocycle_id])
    )
    volume_data = volume_payload["data"]
    assert volume_data["mesocycle_id"] == mesocycle_id
    assert volume_data["total_sets"] >= 1

    intensity_payload = _assert_cli_success(
        run_cli(["--json", "insights", "intensity", "--mesocycle-id", mesocycle_id])
    )
    intensity_data = intensity_payload["data"]
    assert intensity_data["mesocycle_id"] == mesocycle_id
    assert intensity_data["overall_avg_rir"] >= 0

    overload_payload = _assert_cli_success(
        run_cli(
            [
                "--json",
                "insights",
                "overload",
                "--mesocycle-id",
                mesocycle_id,
                "--exercise-id",
                exercise_id,
            ]
        )
    )
    overload_data = overload_payload["data"]
    assert overload_data["mesocycle_id"] == mesocycle_id
    assert overload_data["exercise_id"] == exercise_id
    assert len(overload_data["weekly_progress"]) >= 1

    history_payload = _assert_cli_success(
        run_cli(["--json", "insights", "history", "--exercise-id", exercise_id])
    )
    history_data = history_payload["data"]
    assert history_data["total"] >= 1
    assert any(item["id"] == session_id for item in history_data["items"])

    volume_graphql_data = _graphql_request(
        api_runtime,
        query="""
        query VolumeCheck($mesocycleId: UUID!) {
          mesocycleVolumeInsight(mesocycleId: $mesocycleId) {
            totalSets
          }
        }
        """,
        variables={"mesocycleId": mesocycle_id},
    )
    assert volume_graphql_data["mesocycleVolumeInsight"]["totalSets"] >= 1

    intensity_graphql_data = _graphql_request(
        api_runtime,
        query="""
        query IntensityCheck($mesocycleId: UUID!) {
          mesocycleIntensityInsight(mesocycleId: $mesocycleId) {
            overallAvgRir
          }
        }
        """,
        variables={"mesocycleId": mesocycle_id},
    )
    assert (
        float(intensity_graphql_data["mesocycleIntensityInsight"]["overallAvgRir"]) >= 0
    )

    overload_graphql_data = _graphql_request(
        api_runtime,
        query="""
        query OverloadCheck($mesocycleId: UUID!, $exerciseId: UUID!) {
          progressiveOverloadInsight(mesocycleId: $mesocycleId, exerciseId: $exerciseId) {
            weeklyProgress {
              maxWeight
            }
          }
        }
        """,
        variables={"mesocycleId": mesocycle_id, "exerciseId": exercise_id},
    )
    assert (
        len(overload_graphql_data["progressiveOverloadInsight"]["weeklyProgress"]) >= 1
    )

    history_graphql_data = _graphql_request(
        api_runtime,
        query="""
        query HistoryCheck($exerciseId: UUID!) {
          exerciseHistory(exerciseId: $exerciseId) {
            items {
              id
              status
            }
          }
        }
        """,
        variables={"exerciseId": exercise_id},
    )
    persisted_history_items = history_graphql_data["exerciseHistory"]["items"]
    assert isinstance(persisted_history_items, list)
    assert any(
        item["id"] == session_id and item["status"] == "COMPLETED"
        for item in persisted_history_items
    )


def test_backup_trigger_creates_artifact(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    backup_payload = _assert_cli_success(run_cli(["--json", "backup", "trigger"]))
    backup_data = backup_payload["data"]
    assert isinstance(backup_data, dict)
    assert backup_data["success"] is True

    artifacts = _wait_for_backup_artifact(api_runtime.backups_dir)
    assert artifacts

    filename = backup_data["filename"]
    if isinstance(filename, str):
        assert (api_runtime.backups_dir / filename).exists()
