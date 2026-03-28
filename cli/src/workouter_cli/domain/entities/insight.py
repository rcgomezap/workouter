"""Insights domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WeeklyVolume:
    """Weekly set volume by muscle group."""

    week_number: int
    muscle_group_id: str
    muscle_group_name: str
    set_count: int


@dataclass(slots=True, frozen=True)
class MuscleGroupVolume:
    """Volume contribution per muscle group."""

    muscle_group_id: str
    muscle_group_name: str
    total_sets: int


@dataclass(slots=True, frozen=True)
class VolumeInsight:
    """Mesocycle volume insight aggregate."""

    mesocycle_id: str
    weekly_volumes: tuple[WeeklyVolume, ...]
    total_sets: int
    muscle_group_breakdown: tuple[MuscleGroupVolume, ...]


@dataclass(slots=True, frozen=True)
class WeeklyIntensity:
    """Weekly intensity trend."""

    week_number: int
    avg_rir: float


@dataclass(slots=True, frozen=True)
class IntensityInsight:
    """Mesocycle intensity insight aggregate."""

    mesocycle_id: str
    weekly_intensities: tuple[WeeklyIntensity, ...]
    overall_avg_rir: float


@dataclass(slots=True, frozen=True)
class WeeklyExerciseProgress:
    """Exercise progression metrics for one week."""

    week_number: int
    max_weight: float
    avg_reps: float
    avg_rir: float


@dataclass(slots=True, frozen=True)
class ProgressiveOverloadInsight:
    """Progressive overload trend for one exercise in mesocycle."""

    exercise_id: str
    mesocycle_id: str
    weekly_progress: tuple[WeeklyExerciseProgress, ...]
    estimated_one_rep_max_progression: tuple[float, ...]
