"""Exercise domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MuscleGroup:
    """Exercise muscle group entity."""

    id: str
    name: str


@dataclass(slots=True, frozen=True)
class ExerciseMuscleGroup:
    """Muscle group assignment for an exercise."""

    muscle_group: MuscleGroup
    role: str


@dataclass(slots=True, frozen=True)
class Exercise:
    """Exercise aggregate root."""

    id: str
    name: str
    description: str | None
    equipment: str | None
    muscle_groups: tuple[ExerciseMuscleGroup, ...]
