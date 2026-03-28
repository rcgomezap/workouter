"""GraphQL queries package."""

from workouter_cli.infrastructure.graphql.queries.bodyweight import LIST_BODYWEIGHT_LOGS
from workouter_cli.infrastructure.graphql.queries.exercise import GET_EXERCISE, LIST_EXERCISES
from workouter_cli.infrastructure.graphql.queries.calendar import CALENDAR_DAY, CALENDAR_RANGE
from workouter_cli.infrastructure.graphql.queries.insight import (
    EXERCISE_HISTORY,
    MESOCYCLE_INTENSITY_INSIGHT,
    MESOCYCLE_VOLUME_INSIGHT,
    PROGRESSIVE_OVERLOAD_INSIGHT,
)
from workouter_cli.infrastructure.graphql.queries.mesocycle import GET_MESOCYCLE, LIST_MESOCYCLES
from workouter_cli.infrastructure.graphql.queries.routine import ROUTINE_FIELDS
from workouter_cli.infrastructure.graphql.queries.session import GET_SESSION, LIST_SESSIONS

__all__ = [
    "LIST_BODYWEIGHT_LOGS",
    "GET_EXERCISE",
    "LIST_EXERCISES",
    "CALENDAR_DAY",
    "CALENDAR_RANGE",
    "MESOCYCLE_VOLUME_INSIGHT",
    "MESOCYCLE_INTENSITY_INSIGHT",
    "PROGRESSIVE_OVERLOAD_INSIGHT",
    "EXERCISE_HISTORY",
    "LIST_MESOCYCLES",
    "GET_MESOCYCLE",
    "ROUTINE_FIELDS",
    "LIST_SESSIONS",
    "GET_SESSION",
]
