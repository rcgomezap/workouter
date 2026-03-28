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


def _routine_payload() -> dict[str, object]:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Push Day",
        "description": "Chest/Shoulders/Triceps",
        "exercises": [],
    }


def _routine_exercise_payload() -> dict[str, object]:
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


def _routine_set_payload() -> dict[str, object]:
    return {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "setNumber": 1,
        "setType": "STANDARD",
        "targetRepsMin": 8,
        "targetRepsMax": 10,
        "targetRir": 2,
        "targetWeightKg": 80.0,
        "weightReductionPct": None,
        "restSeconds": 120,
    }


def test_routines_nested_commands_and_remove_validations(mocker) -> None:  # type: ignore[no-untyped-def]
    calls: list[str] = []

    async def fake_execute(self, query: str, variables=None):  # type: ignore[no-untyped-def]
        if "mutation AddRoutineExercise" in query:
            calls.append("add-exercise")
            return {"addRoutineExercise": _routine_payload()}
        if "mutation UpdateRoutineExercise" in query:
            calls.append("update-exercise")
            return {"updateRoutineExercise": _routine_exercise_payload()}
        if "mutation RemoveRoutineExercise" in query:
            calls.append("remove-exercise")
            return {"removeRoutineExercise": True}
        if "mutation AddRoutineSet" in query:
            calls.append("add-set")
            payload = _routine_exercise_payload()
            payload["sets"] = [_routine_set_payload()]
            return {"addRoutineSet": payload}
        if "mutation UpdateRoutineSet" in query:
            calls.append("update-set")
            return {"updateRoutineSet": _routine_set_payload()}
        if "mutation RemoveRoutineSet" in query:
            calls.append("remove-set")
            return {"removeRoutineSet": True}
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
            "routines",
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
            "routines",
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
            "routines",
            "update-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        ],
    )
    assert update_exercise_validation.exit_code == 1

    update_exercise = runner.invoke(
        cli,
        [
            "--json",
            "routines",
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
            "routines",
            "remove-exercise",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        ],
    )
    assert remove_exercise_validation.exit_code == 1

    remove_exercise = runner.invoke(
        cli,
        [
            "--json",
            "routines",
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
            "routines",
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
            "routines",
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
        ["--json", "routines", "update-set", "cccccccc-cccc-cccc-cccc-cccccccccccc"],
    )
    assert update_set_validation.exit_code == 1

    update_set = runner.invoke(
        cli,
        [
            "--json",
            "routines",
            "update-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--target-reps-max",
            "12",
        ],
    )
    assert update_set.exit_code == 0

    invalid_rep_range = runner.invoke(
        cli,
        [
            "--json",
            "routines",
            "update-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--target-reps-min",
            "12",
            "--target-reps-max",
            "10",
        ],
    )
    assert invalid_rep_range.exit_code == 1

    remove_set_validation = runner.invoke(
        cli,
        ["--json", "routines", "remove-set", "cccccccc-cccc-cccc-cccc-cccccccccccc"],
    )
    assert remove_set_validation.exit_code == 1

    remove_set = runner.invoke(
        cli,
        [
            "--json",
            "routines",
            "remove-set",
            "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "--force",
        ],
    )
    assert remove_set.exit_code == 0

    assert calls == [
        "add-exercise",
        "update-exercise",
        "remove-exercise",
        "add-set",
        "update-set",
        "remove-set",
    ]


def test_routines_invalid_option_values_fail_fast() -> None:
    runner = CliRunner(env=_base_env())

    invalid_add_set = runner.invoke(
        cli,
        [
            "--json",
            "routines",
            "add-set",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "--set-number",
            "0",
            "--set-type",
            "STANDARD",
        ],
    )
    assert invalid_add_set.exit_code == 2
    assert "0 is not in the range x>=1" in invalid_add_set.output
