"""GraphQL mutations package."""

from workouter_cli.infrastructure.graphql.mutations.exercise import (
    CREATE_EXERCISE,
    DELETE_EXERCISE,
    UPDATE_EXERCISE,
)

__all__ = ["CREATE_EXERCISE", "UPDATE_EXERCISE", "DELETE_EXERCISE"]
