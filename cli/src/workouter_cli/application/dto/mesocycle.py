"""Mesocycle input DTOs."""

from __future__ import annotations

from datetime import date as dt_date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateMesocycleInputDTO(BaseModel):
    """Validated payload for creating a mesocycle."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: dt_date = Field(alias="startDate")

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
    start_date: dt_date | None = Field(default=None, alias="startDate")
    end_date: dt_date | None = Field(default=None, alias="endDate")
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


class AddMesocycleWeekInputDTO(BaseModel):
    """Validated payload for adding a mesocycle week."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    week_number: int = Field(alias="weekNumber", ge=1)
    week_type: str = Field(alias="weekType")
    start_date: dt_date = Field(alias="startDate")
    end_date: dt_date = Field(alias="endDate")

    @field_validator("week_type")
    @classmethod
    def validate_week_type(cls, value: str) -> str:
        allowed = {"TRAINING", "DELOAD"}
        if value not in allowed:
            msg = "Week type must be one of: TRAINING, DELOAD"
            raise ValueError(msg)
        return value


class UpdateMesocycleWeekInputDTO(BaseModel):
    """Validated payload for updating a mesocycle week."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    week_number: int | None = Field(default=None, alias="weekNumber", ge=1)
    week_type: str | None = Field(default=None, alias="weekType")
    start_date: dt_date | None = Field(default=None, alias="startDate")
    end_date: dt_date | None = Field(default=None, alias="endDate")

    @field_validator("week_type")
    @classmethod
    def validate_optional_week_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        allowed = {"TRAINING", "DELOAD"}
        if value not in allowed:
            msg = "Week type must be one of: TRAINING, DELOAD"
            raise ValueError(msg)
        return value


class AddPlannedSessionInputDTO(BaseModel):
    """Validated payload for adding a planned session."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    routine_id: str | None = Field(default=None, alias="routineId")
    day_of_week: int = Field(alias="dayOfWeek", ge=1, le=7)
    date: dt_date | None = None
    notes: str | None = None


class UpdatePlannedSessionInputDTO(BaseModel):
    """Validated payload for updating a planned session."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, populate_by_name=True)

    routine_id: str | None = Field(default=None, alias="routineId")
    day_of_week: int | None = Field(default=None, alias="dayOfWeek", ge=1, le=7)
    date: dt_date | None = None
    notes: str | None = None
