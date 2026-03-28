"""GraphQL queries package."""

from workouter_cli.infrastructure.graphql.queries.exercise import GET_EXERCISE, LIST_EXERCISES
from workouter_cli.infrastructure.graphql.queries.calendar import CALENDAR_DAY
from workouter_cli.infrastructure.graphql.queries.routine import ROUTINE_FIELDS
from workouter_cli.infrastructure.graphql.queries.session import GET_SESSION, LIST_SESSIONS

__all__ = [
    "GET_EXERCISE",
    "LIST_EXERCISES",
    "CALENDAR_DAY",
    "ROUTINE_FIELDS",
    "LIST_SESSIONS",
    "GET_SESSION",
]
