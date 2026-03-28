"""GraphQL response mappers."""

from __future__ import annotations

from typing import Any

from workouter_cli.domain.entities.exercise import Exercise, ExerciseMuscleGroup, MuscleGroup
from workouter_cli.domain.entities.calendar import CalendarDay, PlannedSession
from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet


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


def map_session_set(data: dict[str, Any]) -> SessionSet:
    """Map GraphQL session set payload to domain entity."""

    return SessionSet(
        id=str(data["id"]),
        set_number=int(data["setNumber"]),
        set_type=str(data["setType"]),
        target_reps=int(data["targetReps"]) if data.get("targetReps") is not None else None,
        target_rir=int(data["targetRir"]) if data.get("targetRir") is not None else None,
        target_weight_kg=(
            float(data["targetWeightKg"]) if data.get("targetWeightKg") is not None else None
        ),
        actual_reps=int(data["actualReps"]) if data.get("actualReps") is not None else None,
        actual_rir=int(data["actualRir"]) if data.get("actualRir") is not None else None,
        actual_weight_kg=(
            float(data["actualWeightKg"]) if data.get("actualWeightKg") is not None else None
        ),
        weight_reduction_pct=(
            float(data["weightReductionPct"])
            if data.get("weightReductionPct") is not None
            else None
        ),
        rest_seconds=int(data["restSeconds"]) if data.get("restSeconds") is not None else None,
        performed_at=str(data["performedAt"]) if data.get("performedAt") is not None else None,
    )


def map_session_exercise(data: dict[str, Any]) -> SessionExercise:
    """Map GraphQL session exercise payload to domain entity."""

    exercise = data["exercise"]
    return SessionExercise(
        id=str(data["id"]),
        exercise_id=str(exercise["id"]),
        exercise_name=str(exercise["name"]),
        order=int(data["order"]),
        superset_group=(
            int(data["supersetGroup"]) if data.get("supersetGroup") is not None else None
        ),
        rest_seconds=int(data["restSeconds"]) if data.get("restSeconds") is not None else None,
        notes=str(data["notes"]) if data.get("notes") is not None else None,
        sets=tuple(map_session_set(item) for item in data.get("sets", [])),
    )


def map_session(data: dict[str, Any]) -> Session:
    """Map GraphQL session payload to domain entity."""

    return Session(
        id=str(data["id"]),
        planned_session_id=(
            str(data["plannedSessionId"]) if data.get("plannedSessionId") is not None else None
        ),
        mesocycle_id=str(data["mesocycleId"]) if data.get("mesocycleId") is not None else None,
        routine_id=str(data["routineId"]) if data.get("routineId") is not None else None,
        status=str(data["status"]),
        started_at=str(data["startedAt"]) if data.get("startedAt") is not None else None,
        completed_at=(str(data["completedAt"]) if data.get("completedAt") is not None else None),
        notes=str(data["notes"]) if data.get("notes") is not None else None,
        exercises=tuple(map_session_exercise(item) for item in data.get("exercises", [])),
    )


def map_routine_set(data: dict[str, Any]) -> RoutineSet:
    """Map GraphQL routine set payload to domain entity."""

    return RoutineSet(
        id=str(data["id"]),
        set_number=int(data["setNumber"]),
        set_type=str(data["setType"]),
        target_reps_min=(
            int(data["targetRepsMin"]) if data.get("targetRepsMin") is not None else None
        ),
        target_reps_max=(
            int(data["targetRepsMax"]) if data.get("targetRepsMax") is not None else None
        ),
        target_rir=int(data["targetRir"]) if data.get("targetRir") is not None else None,
        target_weight_kg=(
            float(data["targetWeightKg"]) if data.get("targetWeightKg") is not None else None
        ),
        weight_reduction_pct=(
            float(data["weightReductionPct"])
            if data.get("weightReductionPct") is not None
            else None
        ),
        rest_seconds=int(data["restSeconds"]) if data.get("restSeconds") is not None else None,
    )


def map_routine_exercise(data: dict[str, Any]) -> RoutineExercise:
    """Map GraphQL routine exercise payload to domain entity."""

    exercise = data["exercise"]
    return RoutineExercise(
        id=str(data["id"]),
        exercise_id=str(exercise["id"]),
        exercise_name=str(exercise["name"]),
        order=int(data["order"]),
        superset_group=(
            int(data["supersetGroup"]) if data.get("supersetGroup") is not None else None
        ),
        rest_seconds=int(data["restSeconds"]) if data.get("restSeconds") is not None else None,
        notes=str(data["notes"]) if data.get("notes") is not None else None,
        sets=tuple(map_routine_set(item) for item in data.get("sets", [])),
    )


def map_routine(data: dict[str, Any]) -> Routine:
    """Map GraphQL routine payload to domain entity."""

    return Routine(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data["description"]) if data.get("description") is not None else None,
        exercises=tuple(map_routine_exercise(item) for item in data.get("exercises", [])),
    )


def map_calendar_day(data: dict[str, Any]) -> CalendarDay:
    """Map GraphQL calendar day payload to domain entity."""

    planned_session_data = data.get("plannedSession")
    planned_session: PlannedSession | None
    if planned_session_data is None:
        planned_session = None
    else:
        routine = planned_session_data.get("routine")
        planned_session = PlannedSession(
            id=str(planned_session_data["id"]),
            routine_id=str(routine["id"]) if routine is not None else None,
            routine_name=str(routine["name"]) if routine is not None else None,
            day_of_week=int(planned_session_data["dayOfWeek"]),
            date=str(planned_session_data["date"]),
            notes=(
                str(planned_session_data["notes"])
                if planned_session_data.get("notes") is not None
                else None
            ),
        )

    session_data = data.get("session")
    session_id = str(session_data["id"]) if session_data is not None else None
    return CalendarDay(
        date=str(data["date"]),
        planned_session=planned_session,
        session_id=session_id,
        is_completed=bool(data["isCompleted"]),
        is_rest_day=bool(data["isRestDay"]),
    )
