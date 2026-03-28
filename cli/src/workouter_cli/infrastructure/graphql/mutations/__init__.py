"""GraphQL mutations package."""

from workouter_cli.infrastructure.graphql.mutations.exercise import (
    CREATE_EXERCISE,
    DELETE_EXERCISE,
    UPDATE_EXERCISE,
)
from workouter_cli.infrastructure.graphql.mutations.session import (
    COMPLETE_SESSION,
    CREATE_SESSION,
    LOG_SET_RESULT,
    START_SESSION,
)

__all__ = [
    "CREATE_EXERCISE",
    "UPDATE_EXERCISE",
    "DELETE_EXERCISE",
    "CREATE_SESSION",
    "START_SESSION",
    "COMPLETE_SESSION",
    "LOG_SET_RESULT",
]
