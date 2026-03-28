"""Exercise input/output DTOs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateExerciseInputDTO(BaseModel):
    """Validated payload for creating an exercise."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    equipment: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "Exercise name must not be blank"
            raise ValueError(msg)
        return value


class UpdateExerciseInputDTO(BaseModel):
    """Validated payload for updating an exercise."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    equipment: str | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "Exercise name must not be blank"
            raise ValueError(msg)
        return value
