"""Domain repository protocols package."""

from workouter_cli.domain.repositories.exercise import ExerciseRepository
from workouter_cli.domain.repositories.mesocycle import MesocycleRepository
from workouter_cli.domain.repositories.session import SessionRepository
from workouter_cli.domain.repositories.calendar import CalendarRepository
from workouter_cli.domain.repositories.routine import RoutineRepository

__all__ = [
    "ExerciseRepository",
    "MesocycleRepository",
    "SessionRepository",
    "CalendarRepository",
    "RoutineRepository",
]
