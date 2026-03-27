from workouter_cli.domain.exceptions import (
    APIError,
    AuthError,
    CLIError,
    NetworkError,
    ValidationError,
)
from workouter_cli.utils.exit_codes import ExitCode


def test_cli_error_keeps_message_and_exit_code() -> None:
    error = CLIError(message="boom", exit_code=ExitCode.API_ERROR, code="X")

    assert str(error) == "boom"
    assert error.exit_code == ExitCode.API_ERROR
    assert error.code == "X"


def test_validation_error_defaults() -> None:
    error = ValidationError("bad input")

    assert error.exit_code == ExitCode.USER_ERROR
    assert error.code == "VALIDATION_ERROR"
    assert str(error) == "bad input"


def test_api_error_defaults() -> None:
    error = APIError("api rejected")

    assert error.exit_code == ExitCode.API_ERROR
    assert error.code == "API_ERROR"


def test_auth_error_defaults() -> None:
    error = AuthError("unauthorized")

    assert error.exit_code == ExitCode.AUTH_ERROR
    assert error.code == "AUTH_ERROR"


def test_network_error_defaults() -> None:
    error = NetworkError("timeout")

    assert error.exit_code == ExitCode.NETWORK_ERROR
    assert error.code == "NETWORK_ERROR"
