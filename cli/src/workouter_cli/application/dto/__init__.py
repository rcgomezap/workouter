"""Application DTO package."""

from workouter_cli.application.dto.exercise import CreateExerciseInputDTO, UpdateExerciseInputDTO
from workouter_cli.application.dto.pagination import PaginationInput, PaginationResult

__all__ = [
    "CreateExerciseInputDTO",
    "UpdateExerciseInputDTO",
    "PaginationInput",
    "PaginationResult",
]
