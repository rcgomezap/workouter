import strawberry
from uuid import UUID
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.insight import (
    VolumeInsight,
    WeeklyVolume,
    MuscleGroupVolume,
    ProgressiveOverloadInsight,
    WeeklyExerciseProgress,
    IntensityInsight,
    WeeklyIntensity,
)
from app.presentation.graphql.types.session import PaginatedSessions, Session
from app.presentation.graphql.types.enums import SessionStatus as SessionStatusType
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.application.dto.pagination import PaginationInput as PaginationDTO


def map_volume_insight(v) -> VolumeInsight:
    return VolumeInsight(
        mesocycle_id=v.mesocycle_id,
        weekly_volumes=[
            WeeklyVolume(week_number=wv.week_number, set_count=wv.sets_count)
            for wv in v.weekly_volumes
        ],
        total_sets=v.total_sets,
        muscle_group_breakdown=[
            MuscleGroupVolume(
                muscle_group_id=mgv.muscle_group_id,
                muscle_group_name=mgv.muscle_group_name,
                total_sets=mgv.sets_count,
            )
            for mgv in v.muscle_group_breakdown
        ],
    )


def map_progressive_overload_insight(p) -> ProgressiveOverloadInsight:
    return ProgressiveOverloadInsight(
        exercise_id=p.exercise_id,
        mesocycle_id=p.mesocycle_id,
        weekly_progress=[
            WeeklyExerciseProgress(
                week_number=wp.week_number,
                max_weight=wp.max_weight_kg,
                avg_reps=wp.avg_reps,
                avg_rir=wp.avg_rir,
            )
            for wp in p.weekly_progress
        ],
        estimated_one_rep_max_progression=p.estimated_one_rep_max_progression,
    )


@strawberry.type
class InsightQuery:
    @strawberry.field
    async def mesocycle_volume_insight(
        self, info: Info[Context, None], mesocycle_id: UUID, muscle_group_id: UUID | None = None
    ) -> VolumeInsight:
        v = await info.context.insight_service.get_volume_insight(mesocycle_id, muscle_group_id)
        return map_volume_insight(v)

    @strawberry.field
    async def progressive_overload_insight(
        self, info: Info[Context, None], mesocycle_id: UUID, exercise_id: UUID
    ) -> ProgressiveOverloadInsight:
        p = await info.context.insight_service.get_progressive_overload_insight(
            mesocycle_id, exercise_id
        )
        return map_progressive_overload_insight(p)

    @strawberry.field
    async def mesocycle_intensity_insight(
        self, info: Info[Context, None], mesocycle_id: UUID
    ) -> IntensityInsight:
        i = await info.context.insight_service.get_intensity_insight(mesocycle_id)
        return IntensityInsight(
            mesocycle_id=i.mesocycle_id,
            weekly_intensities=[
                WeeklyIntensity(week_number=wi.week_number, avg_rir=wi.avg_rir)
                for wi in i.weekly_intensities
            ],
            overall_avg_rir=i.overall_avg_rir,
        )

    @strawberry.field
    async def exercise_history(
        self,
        info: Info[Context, None],
        exercise_id: UUID,
        routine_id: UUID | None = None,
        pagination: PaginationInput | None = None,
    ) -> PaginatedSessions:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )
        result = await info.context.insight_service.get_exercise_history(
            exercise_id, p_dto, routine_id=routine_id
        )
        return PaginatedSessions(
            items=[
                Session(
                    id=s.id,
                    planned_session_id=s.planned_session_id,
                    mesocycle_id=s.mesocycle_id,
                    routine_id=s.routine_id,
                    status=SessionStatusType(s.status.value),
                    started_at=s.started_at,
                    completed_at=s.completed_at,
                    notes=s.notes,
                    exercises=[],
                )
                for s in result.items
            ],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )
