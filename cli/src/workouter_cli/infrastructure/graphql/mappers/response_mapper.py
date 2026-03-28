"""GraphQL response mappers."""

from __future__ import annotations

from typing import Any

from workouter_cli.domain.entities.exercise import Exercise, ExerciseMuscleGroup, MuscleGroup


def map_exercise(data: dict[str, Any]) -> Exercise:
    """Map GraphQL exercise payload to domain entity."""

    muscle_groups = tuple(map_exercise_muscle_group(item) for item in data.get("muscleGroups", []))
    return Exercise(
        id=str(data["id"]),
        name=str(data["name"]),
        description=data.get("description"),
        equipment=data.get("equipment"),
        muscle_groups=muscle_groups,
    )


def map_exercise_muscle_group(data: dict[str, Any]) -> ExerciseMuscleGroup:
    """Map nested exercise muscle group payload."""

    muscle_group_data = data["muscleGroup"]
    muscle_group = MuscleGroup(
        id=str(muscle_group_data["id"]),
        name=str(muscle_group_data["name"]),
    )
    return ExerciseMuscleGroup(muscle_group=muscle_group, role=str(data["role"]))
