"""Application DTO package."""

from workouter_cli.application.dto.exercise import CreateExerciseInputDTO, UpdateExerciseInputDTO
from workouter_cli.application.dto.pagination import PaginationInput, PaginationResult
from workouter_cli.application.dto.routine import CreateRoutineInputDTO, UpdateRoutineInputDTO

__all__ = [
    "CreateExerciseInputDTO",
    "UpdateExerciseInputDTO",
    "CreateRoutineInputDTO",
    "UpdateRoutineInputDTO",
    "PaginationInput",
    "PaginationResult",
]
