from __future__ import annotations

import json
from collections.abc import Callable
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
