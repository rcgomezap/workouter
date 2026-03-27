"""Domain exceptions with semantic exit codes."""

from workouter_cli.utils.exit_codes import ExitCode


class CLIError(Exception):
    """Base exception for CLI failures with a semantic exit code."""

    def __init__(self, message: str, exit_code: ExitCode, code: str = "CLI_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.code = code

    def __str__(self) -> str:
        return self.message


class ValidationError(CLIError):
    """Raised when user-provided input is invalid."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message=message, exit_code=ExitCode.USER_ERROR, code=code)


class APIError(CLIError):
    """Raised when the API rejects a valid request."""

    def __init__(self, message: str, code: str = "API_ERROR") -> None:
        super().__init__(message=message, exit_code=ExitCode.API_ERROR, code=code)


class AuthError(CLIError):
    """Raised when authentication or authorization fails."""

    def __init__(self, message: str, code: str = "AUTH_ERROR") -> None:
        super().__init__(message=message, exit_code=ExitCode.AUTH_ERROR, code=code)


class NetworkError(CLIError):
    """Raised when network or transport failures happen."""

    def __init__(self, message: str, code: str = "NETWORK_ERROR") -> None:
        super().__init__(message=message, exit_code=ExitCode.NETWORK_ERROR, code=code)
