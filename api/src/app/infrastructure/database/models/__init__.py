"""
Import all models to ensure SQLAlchemy can resolve relationships.
This must be imported before any operations that use Base.metadata.
"""

from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.bodyweight import BodyweightLogTable
from app.infrastructure.database.models.exercise import ExerciseTable, exercise_muscle_group
from app.infrastructure.database.models.mesocycle import MesocycleTable, MesocycleWeekTable
from app.infrastructure.database.models.muscle_group import MuscleGroupTable
from app.infrastructure.database.models.routine import (
    RoutineExerciseTable,
    RoutineSetTable,
    RoutineTable,
)
from app.infrastructure.database.models.session import (
    PlannedSessionTable,
    SessionExerciseTable,
    SessionSetTable,
    SessionTable,
)

__all__ = [
    "Base",
    "BodyweightLogTable",
    "ExerciseTable",
    "MesocycleTable",
    "MesocycleWeekTable",
    "MuscleGroupTable",
    "PlannedSessionTable",
    "RoutineExerciseTable",
    "RoutineSetTable",
    "RoutineTable",
    "SessionExerciseTable",
    "SessionSetTable",
    "SessionTable",
    "exercise_muscle_group",
]
