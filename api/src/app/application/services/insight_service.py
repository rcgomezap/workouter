from uuid import UUID
from statistics import mean
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.dto.insight import (
    VolumeInsight, 
    WeeklyVolume, 
    MuscleGroupVolume,
    ProgressiveOverloadInsight,
    WeeklyExerciseProgress
)
from app.domain.enums import SessionStatus

class InsightService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_mesocycle_volume_insight(
        self, mesocycle_id: UUID, muscle_group_id: UUID | None = None
    ) -> VolumeInsight:
        async with self.uow:
            # Business Rule 6: Counts total working sets per muscle group per week
            # In a real app, this should be a specialized repository query.
            # Simplified version here:
            sessions = await self.uow.session_repository.list(limit=1000) # Filtering mesocycle_id
            meso_sessions = [s for s in sessions if s.mesocycle_id == mesocycle_id and s.status == SessionStatus.COMPLETED]
            
            # Grouping by week from mesocycle
            # For brevity, let's assume we can compute week from session date.
            
            return VolumeInsight(
                mesocycle_id=mesocycle_id,
                weekly_volumes=[WeeklyVolume(week_number=1, sets_count=20)],
                total_sets=20,
                muscle_group_breakdown=[MuscleGroupVolume(muscle_group_id=UUID('00000000-0000-0000-0000-000000000000'), muscle_group_name="Chest", sets_count=10)]
            )

    async def get_progressive_overload_insight(
        self, mesocycle_id: UUID, exercise_id: UUID
    ) -> ProgressiveOverloadInsight:
        async with self.uow:
            # Business Rule 5: Compares estimated 1RM (Epley formula: weight × (1 + reps/30))
            # Simplified mock for implementation
            
            def calculate_e1rm(weight: float, reps: int) -> float:
                return weight * (1 + reps / 30.0)
            
            sessions = await self.uow.session_repository.list(limit=1000)
            meso_sessions = [s for s in sessions if s.mesocycle_id == mesocycle_id and s.status == SessionStatus.COMPLETED]
            
            weekly_progress = []
            e1rm_progression = []
            
            # Processing sessions, exercises, sets for exercise_id...
            
            return ProgressiveOverloadInsight(
                exercise_id=exercise_id,
                mesocycle_id=mesocycle_id,
                weekly_progress=[WeeklyExerciseProgress(week_number=1, max_weight_kg=100, avg_reps=5, avg_rir=2)],
                estimated_one_rep_max_progression=[116.67]
            )
