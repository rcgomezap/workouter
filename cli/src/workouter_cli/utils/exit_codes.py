"""Semantic CLI exit codes."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit code contract for automation and users."""

    SUCCESS = 0
    USER_ERROR = 1
    API_ERROR = 2
    AUTH_ERROR = 3
    NETWORK_ERROR = 4
