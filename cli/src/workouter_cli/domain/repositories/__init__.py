"""Domain repository protocols package."""

from workouter_cli.domain.repositories.backup import BackupRepository
from workouter_cli.domain.repositories.bodyweight import BodyweightRepository
from workouter_cli.domain.repositories.exercise import ExerciseRepository
from workouter_cli.domain.repositories.insight import InsightRepository
from workouter_cli.domain.repositories.mesocycle import MesocycleRepository
from workouter_cli.domain.repositories.session import SessionRepository
from workouter_cli.domain.repositories.calendar import CalendarRepository
from workouter_cli.domain.repositories.routine import RoutineRepository

__all__ = [
    "BackupRepository",
    "BodyweightRepository",
    "ExerciseRepository",
    "InsightRepository",
    "MesocycleRepository",
    "SessionRepository",
    "CalendarRepository",
    "RoutineRepository",
]
