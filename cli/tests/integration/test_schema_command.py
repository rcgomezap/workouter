from __future__ import annotations

import json

from click.testing import CliRunner

from workouter_cli.main import cli


def test_schema_command_outputs_valid_json_for_exercises_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "exercises list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "exercises list"
    assert payload["description"] == "List exercises."

    options = {item["name"] for item in payload["options"]}
    assert "--page" in options
    assert "--muscle-group-id" in options


def test_schema_command_outputs_valid_json_for_routines_add_exercise() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "routines add-exercise"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "routines add-exercise"
    assert payload["description"] == "Add exercise to a routine."

    options = {item["name"] for item in payload["options"]}
    assert "--exercise-id" in options
    assert "--order" in options


def test_schema_command_outputs_valid_json_for_routines_crud_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "routines list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "routines list"
    assert payload["description"] == "List routines."

    options = {item["name"] for item in payload["options"]}
    assert "--page" in options
    assert "--page-size" in options


def test_schema_command_outputs_valid_json_for_mesocycles_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "mesocycles list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "mesocycles list"
    assert payload["description"] == "List mesocycles."

    options = {item["name"] for item in payload["options"]}
    assert "--page" in options
    assert "--status" in options


def test_schema_command_outputs_valid_json_for_mesocycles_add_week() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "mesocycles add-week"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "mesocycles add-week"
    assert payload["description"] == "Add one planning week to a mesocycle."

    options = {item["name"] for item in payload["options"]}
    assert "--week-number" in options
    assert "--week-type" in options


def test_schema_command_outputs_valid_json_for_mesocycles_add_session() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "mesocycles add-session"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "mesocycles add-session"
    assert payload["description"] == "Add one planned session to a mesocycle week."

    options = {item["name"] for item in payload["options"]}
    assert "--day-of-week" in options
    assert "--routine-id" in options


def test_schema_command_outputs_valid_json_for_bodyweight_log() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "bodyweight log"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "bodyweight log"
    assert payload["description"] == "Log bodyweight."

    options = {item["name"] for item in payload["options"]}
    assert "--weight" in options
    assert "--recorded-at" in options


def test_schema_command_outputs_valid_json_for_insights_volume() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "insights volume"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "insights volume"
    assert payload["description"] == "Show mesocycle volume insight."

    options = {item["name"] for item in payload["options"]}
    assert "--mesocycle-id" in options


def test_schema_command_outputs_valid_json_for_calendar_range() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "calendar range"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "calendar range"
    assert payload["description"] == "Show calendar range."

    options = {item["name"] for item in payload["options"]}
    assert "--start-date" in options
    assert "--end-date" in options


def test_schema_command_outputs_valid_json_for_backup_trigger() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "backup trigger"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "backup trigger"
    assert payload["description"] == "Trigger database backup."
