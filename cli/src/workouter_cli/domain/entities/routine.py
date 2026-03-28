"""Routine domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RoutineSet:
    """Routine set prescription details."""

    id: str
    set_number: int
    set_type: str
    target_reps_min: int | None
    target_reps_max: int | None
    target_rir: int | None
    target_weight_kg: float | None
    weight_reduction_pct: float | None
    rest_seconds: int | None


@dataclass(slots=True, frozen=True)
class RoutineExercise:
    """Exercise entry inside a routine."""

    id: str
    exercise_id: str
    exercise_name: str
    order: int
    superset_group: int | None
    rest_seconds: int | None
    notes: str | None
    sets: tuple[RoutineSet, ...]


@dataclass(slots=True, frozen=True)
class Routine:
    """Routine aggregate root."""

    id: str
    name: str
    description: str | None
    exercises: tuple[RoutineExercise, ...]
