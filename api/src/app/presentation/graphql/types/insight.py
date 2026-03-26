from uuid import UUID

import strawberry


@strawberry.type
class WeeklyVolume:
    week_number: int
    set_count: int


@strawberry.type
class MuscleGroupVolume:
    muscle_group_id: UUID
    muscle_group_name: str
    total_sets: int


@strawberry.type
class VolumeInsight:
    mesocycle_id: UUID
    weekly_volumes: list[WeeklyVolume]
    total_sets: int
    muscle_group_breakdown: list[MuscleGroupVolume]


@strawberry.type
class WeeklyExerciseProgress:
    week_number: int
    max_weight: float
    avg_reps: float
    avg_rir: float


@strawberry.type
class ProgressiveOverloadInsight:
    exercise_id: UUID
    mesocycle_id: UUID
    weekly_progress: list[WeeklyExerciseProgress]
    estimated_one_rep_max_progression: list[float]


@strawberry.type
class WeeklyIntensity:
    week_number: int
    avg_rir: float


@strawberry.type
class IntensityInsight:
    mesocycle_id: UUID
    weekly_intensities: list[WeeklyIntensity]
    overall_avg_rir: float
