"""GraphQL queries package."""

from workouter_cli.infrastructure.graphql.queries.exercise import GET_EXERCISE, LIST_EXERCISES
from workouter_cli.infrastructure.graphql.queries.calendar import CALENDAR_DAY

__all__ = ["GET_EXERCISE", "LIST_EXERCISES", "CALENDAR_DAY"]
