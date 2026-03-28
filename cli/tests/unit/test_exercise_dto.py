import pytest
from pydantic import ValidationError

from workouter_cli.application.dto.exercise import CreateExerciseInputDTO


def test_create_exercise_dto_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        CreateExerciseInputDTO(name="   ")


def test_create_exercise_dto_rejects_name_over_200_chars() -> None:
    with pytest.raises(ValidationError):
        CreateExerciseInputDTO(name="x" * 201)
