"""Session domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SessionSet:
    """Workout session set details."""

    id: str
    set_number: int
    set_type: str
    target_reps: int | None
    target_rir: int | None
    target_weight_kg: float | None
    actual_reps: int | None
    actual_rir: int | None
    actual_weight_kg: float | None
    weight_reduction_pct: float | None
    rest_seconds: int | None
    performed_at: str | None


@dataclass(slots=True, frozen=True)
class SessionExercise:
    """Exercise entry inside a session."""

    id: str
    exercise_id: str
    exercise_name: str
    order: int
    superset_group: int | None
    rest_seconds: int | None
    notes: str | None
    sets: tuple[SessionSet, ...]


@dataclass(slots=True, frozen=True)
class Session:
    """Session aggregate root."""

    id: str
    planned_session_id: str | None
    mesocycle_id: str | None
    routine_id: str | None
    status: str
    started_at: str | None
    completed_at: str | None
    notes: str | None
    exercises: tuple[SessionExercise, ...]
