"""GraphQL response mappers."""

from __future__ import annotations

from typing import Any

from workouter_cli.domain.entities.backup import BackupResult
from workouter_cli.domain.entities.bodyweight import BodyweightLog
from workouter_cli.domain.entities.exercise import Exercise, ExerciseMuscleGroup, MuscleGroup
from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    MuscleGroupVolume,
    ProgressiveOverloadInsight,
    VolumeInsight,
    WeeklyExerciseProgress,
    WeeklyIntensity,
    WeeklyVolume,
)
from workouter_cli.domain.entities.calendar import CalendarDay, PlannedSession
from workouter_cli.domain.entities.mesocycle import (
    Mesocycle,
    MesocyclePlannedSession,
    MesocycleWeek,
)
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


def map_mesocycle_week(data: dict[str, Any]) -> MesocycleWeek:
    """Map GraphQL mesocycle week payload to domain entity."""

    return MesocycleWeek(
        id=str(data["id"]),
        week_number=int(data["weekNumber"]),
        week_type=str(data["weekType"]),
        start_date=str(data["startDate"]),
        end_date=str(data["endDate"]),
        planned_sessions=tuple(
            map_mesocycle_planned_session(item) for item in data.get("plannedSessions", [])
        ),
    )


def map_mesocycle_planned_session(data: dict[str, Any]) -> MesocyclePlannedSession:
    """Map GraphQL mesocycle planned session payload to domain entity."""

    routine = data.get("routine")
    return MesocyclePlannedSession(
        id=str(data["id"]),
        routine_id=str(routine["id"]) if routine is not None else None,
        routine_name=str(routine["name"]) if routine is not None else None,
        day_of_week=int(data["dayOfWeek"]),
        date=str(data["date"]),
        notes=str(data["notes"]) if data.get("notes") is not None else None,
    )


def map_mesocycle(data: dict[str, Any]) -> Mesocycle:
    """Map GraphQL mesocycle payload to domain entity."""

    return Mesocycle(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data["description"]) if data.get("description") is not None else None,
        start_date=str(data["startDate"]),
        end_date=str(data["endDate"]) if data.get("endDate") is not None else None,
        status=str(data["status"]),
        weeks=tuple(map_mesocycle_week(item) for item in data.get("weeks", [])),
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


def map_bodyweight_log(data: dict[str, Any]) -> BodyweightLog:
    """Map GraphQL bodyweight log payload to domain entity."""

    return BodyweightLog(
        id=str(data["id"]),
        weight_kg=float(data["weightKg"]),
        recorded_at=str(data["recordedAt"]),
        notes=str(data["notes"]) if data.get("notes") is not None else None,
        created_at=str(data["createdAt"]),
    )


def map_weekly_volume(data: dict[str, Any]) -> WeeklyVolume:
    """Map weekly volume payload."""

    return WeeklyVolume(
        week_number=int(data["weekNumber"]),
        muscle_group_id=str(data["muscleGroupId"]),
        muscle_group_name=str(data["muscleGroupName"]),
        set_count=int(data["setCount"]),
    )


def map_muscle_group_volume(data: dict[str, Any]) -> MuscleGroupVolume:
    """Map muscle group volume payload."""

    return MuscleGroupVolume(
        muscle_group_id=str(data["muscleGroupId"]),
        muscle_group_name=str(data["muscleGroupName"]),
        total_sets=int(data["totalSets"]),
    )


def map_volume_insight(data: dict[str, Any]) -> VolumeInsight:
    """Map volume insight payload."""

    return VolumeInsight(
        mesocycle_id=str(data["mesocycleId"]),
        weekly_volumes=tuple(map_weekly_volume(item) for item in data.get("weeklyVolumes", [])),
        total_sets=int(data["totalSets"]),
        muscle_group_breakdown=tuple(
            map_muscle_group_volume(item) for item in data.get("muscleGroupBreakdown", [])
        ),
    )


def map_weekly_intensity(data: dict[str, Any]) -> WeeklyIntensity:
    """Map weekly intensity payload."""

    return WeeklyIntensity(
        week_number=int(data["weekNumber"]),
        avg_rir=float(data["avgRir"]),
    )


def map_intensity_insight(data: dict[str, Any]) -> IntensityInsight:
    """Map intensity insight payload."""

    return IntensityInsight(
        mesocycle_id=str(data["mesocycleId"]),
        weekly_intensities=tuple(
            map_weekly_intensity(item) for item in data.get("weeklyIntensities", [])
        ),
        overall_avg_rir=float(data["overallAvgRir"]),
    )


def map_weekly_exercise_progress(data: dict[str, Any]) -> WeeklyExerciseProgress:
    """Map weekly exercise progress payload."""

    return WeeklyExerciseProgress(
        week_number=int(data["weekNumber"]),
        max_weight=float(data["maxWeight"]),
        avg_reps=float(data["avgReps"]),
        avg_rir=float(data["avgRir"]),
    )


def map_progressive_overload_insight(data: dict[str, Any]) -> ProgressiveOverloadInsight:
    """Map progressive overload insight payload."""

    return ProgressiveOverloadInsight(
        exercise_id=str(data["exerciseId"]),
        mesocycle_id=str(data["mesocycleId"]),
        weekly_progress=tuple(
            map_weekly_exercise_progress(item) for item in data.get("weeklyProgress", [])
        ),
        estimated_one_rep_max_progression=tuple(
            float(item) for item in data.get("estimatedOneRepMaxProgression", [])
        ),
    )


def map_backup_result(data: dict[str, Any]) -> BackupResult:
    """Map backup result payload."""

    return BackupResult(
        success=bool(data["success"]),
        filename=str(data["filename"]) if data.get("filename") is not None else None,
        size_bytes=int(data["sizeBytes"]) if data.get("sizeBytes") is not None else None,
        created_at=str(data["createdAt"]),
    )
