from uuid import UUID
from pydantic import BaseModel

class WeeklyVolume(BaseModel):
    week_number: int
    sets_count: int

class MuscleGroupVolume(BaseModel):
    muscle_group_id: UUID
    muscle_group_name: str
    sets_count: int

class VolumeInsight(BaseModel):
    mesocycle_id: UUID
    weekly_volumes: list[WeeklyVolume]
    total_sets: int
    muscle_group_breakdown: list[MuscleGroupVolume]

class WeeklyExerciseProgress(BaseModel):
    week_number: int
    max_weight_kg: float
    avg_reps: float
    avg_rir: float

class ProgressiveOverloadInsight(BaseModel):
    exercise_id: UUID
    mesocycle_id: UUID
    weekly_progress: list[WeeklyExerciseProgress]
    estimated_one_rep_max_progression: list[float]
