import json

from click.testing import CliRunner

from workouter_cli.main import cli


def test_help_is_available_without_env() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Workouter CLI" in result.output


def test_ping_exits_with_auth_code_when_api_key_missing() -> None:
    runner = CliRunner(env={"WORKOUTER_API_URL": "http://localhost:8000/graphql"})
    result = runner.invoke(cli, ["ping"])

    assert result.exit_code == 3
    assert "WORKOUTER_API_KEY" in result.stderr


def test_ping_exits_with_user_error_when_url_is_invalid() -> None:
    runner = CliRunner(
        env={
            "WORKOUTER_API_URL": "invalid-url",
            "WORKOUTER_API_KEY": "test-api-key",
        }
    )
    result = runner.invoke(cli, ["ping"])

    assert result.exit_code == 1
    assert "Invalid CLI configuration" in result.stderr


def test_ping_with_valid_env_returns_ready() -> None:
    runner = CliRunner(
        env={
            "WORKOUTER_API_URL": "http://localhost:8000/graphql",
            "WORKOUTER_API_KEY": "test-api-key",
            "WORKOUTER_CLI_TIMEOUT": "30",
            "WORKOUTER_CLI_LOG_LEVEL": "INFO",
        }
    )
    result = runner.invoke(cli, ["ping"])

    assert result.exit_code == 0
    assert "message" in result.output


def test_ping_json_output_has_expected_shape() -> None:
    runner = CliRunner(
        env={
            "WORKOUTER_API_URL": "http://localhost:8000/graphql",
            "WORKOUTER_API_KEY": "test-api-key",
            "WORKOUTER_CLI_TIMEOUT": "30",
            "WORKOUTER_CLI_LOG_LEVEL": "INFO",
        }
    )
    result = runner.invoke(cli, ["--json", "ping"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["message"] == "ready"


def test_schema_exercises_list_outputs_machine_readable_definition() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "exercises list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["command"] == "exercises list"
    assert payload["description"] == "List exercises."

    option_names = {option["name"] for option in payload["options"]}
    assert "--page" in option_names
    assert "--muscle-group-id" in option_names


def test_schema_unknown_command_fails() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "nope cmd"])

    assert result.exit_code != 0
    assert "Unknown command" in result.output


def test_help_includes_sessions_command_group() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "sessions" in result.output


def test_help_includes_routines_command_group() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "routines" in result.output


def test_help_includes_mesocycles_command_group() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "mesocycles" in result.output


def test_schema_sessions_list_outputs_machine_readable_definition() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "sessions list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["command"] == "sessions list"
    assert payload["description"] == "List sessions."

    option_names = {option["name"] for option in payload["options"]}
    assert "--status" in option_names
    assert "--mesocycle-id" in option_names


def test_schema_routines_add_set_outputs_machine_readable_definition() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "routines add-set"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["command"] == "routines add-set"
    assert payload["description"] == "Add set to a routine exercise."

    option_names = {option["name"] for option in payload["options"]}
    assert "--set-number" in option_names
    assert "--set-type" in option_names


def test_schema_routines_list_outputs_machine_readable_definition() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "routines list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["command"] == "routines list"
    assert payload["description"] == "List routines."

    option_names = {option["name"] for option in payload["options"]}
    assert "--page" in option_names
    assert "--page-size" in option_names


def test_schema_mesocycles_list_outputs_machine_readable_definition() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "mesocycles list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["command"] == "mesocycles list"
    assert payload["description"] == "List mesocycles."

    option_names = {option["name"] for option in payload["options"]}
    assert "--page" in option_names
    assert "--status" in option_names
