import json

from click.testing import CliRunner

from workouter_cli.main import cli


def test_root_help_works() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Workouter CLI" in result.output


def test_global_flags_initialize_context(base_env: dict[str, str]) -> None:
    runner = CliRunner(env=base_env)

    result = runner.invoke(cli, ["--json", "--timeout", "42", "ping"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())
    assert payload["success"] is True
    assert payload["data"]["message"] == "ready"
    assert payload["data"]["timeout"] == 42


def test_auth_error_in_json_mode_returns_exit_code_and_payload(base_env: dict[str, str]) -> None:
    runner = CliRunner(env=base_env)

    result = runner.invoke(cli, ["--json", "raise-auth"])

    assert result.exit_code == 3
    payload = json.loads(result.output.strip())
    assert payload["success"] is False
    assert payload["error"]["code"] == "AUTH_ERROR"
    assert payload["error"]["message"] == "Invalid API key"
