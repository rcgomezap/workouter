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
    assert "WORKOUTER_API_KEY" in result.output


def test_ping_exits_with_user_error_when_url_is_invalid() -> None:
    runner = CliRunner(
        env={
            "WORKOUTER_API_URL": "invalid-url",
            "WORKOUTER_API_KEY": "test-api-key",
        }
    )
    result = runner.invoke(cli, ["ping"])

    assert result.exit_code == 1
    assert "Invalid CLI configuration" in result.output


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
    assert "ready" in result.output
