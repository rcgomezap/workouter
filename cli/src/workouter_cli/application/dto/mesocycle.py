"""Mesocycle input DTOs."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateMesocycleInputDTO(BaseModel):
    """Validated payload for creating a mesocycle."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date = Field(alias="startDate")

    @field_validator("name")
    @classmethod
    def validate_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "Mesocycle name must not be blank"
            raise ValueError(msg)
        return value


class UpdateMesocycleInputDTO(BaseModel):
    """Validated payload for updating a mesocycle."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    status: str | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "Mesocycle name must not be blank"
            raise ValueError(msg)
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        allowed = {"PLANNED", "ACTIVE", "COMPLETED"}
        if value not in allowed:
            msg = "Mesocycle status must be one of: PLANNED, ACTIVE, COMPLETED"
            raise ValueError(msg)
        return value
