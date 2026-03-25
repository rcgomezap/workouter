import strawberry
from uuid import UUID
from datetime import date
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.session import (
    Session,
    SessionExercise,
    SessionSet,
    PaginatedSessions,
)
from app.presentation.graphql.types.enums import SessionStatus
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.application.dto.pagination import PaginationInput as PaginationDTO
from app.presentation.graphql.resolvers.exercise import map_exercise


def map_session_set(s) -> SessionSet:
    return SessionSet(
        id=s.id,
        set_number=s.set_number,
        set_type=s.set_type,
        target_reps=s.target_reps,
        target_rir=s.target_rir,
        target_weight_kg=s.target_weight_kg,
        actual_reps=s.actual_reps,
        actual_rir=s.actual_rir,
        actual_weight_kg=s.actual_weight_kg,
        weight_reduction_pct=s.weight_reduction_pct,
        rest_seconds=s.rest_seconds,
        performed_at=s.performed_at,
    )


def map_session_exercise(se) -> SessionExercise:
    return SessionExercise(
        id=se.id,
        exercise=map_exercise(se.exercise),
        order=se.order,
        superset_group=se.superset_group,
        rest_seconds=se.rest_seconds,
        notes=se.notes,
        sets=[map_session_set(s) for s in se.sets],
    )


def map_session(s) -> Session:
    return Session(
        id=s.id,
        planned_session_id=s.planned_session_id,
        mesocycle_id=s.mesocycle_id,
        routine_id=s.routine_id,
        status=s.status,
        started_at=s.started_at,
        completed_at=s.completed_at,
        notes=s.notes,
        exercises=[map_session_exercise(se) for se in s.exercises],
    )


@strawberry.type
class SessionQuery:
    @strawberry.field
    async def sessions(
        self,
        info: Info[Context, None],
        pagination: PaginationInput | None = None,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> PaginatedSessions:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )
        # SessionService.list_sessions currently only takes pagination
        result = await info.context.session_service.list_sessions(p_dto)
        return PaginatedSessions(
            items=[map_session(s) for s in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )

    @strawberry.field
    async def session(self, info: Info[Context, None], id: UUID) -> Session:
        s = await info.context.session_service.get_session(id)
        return map_session(s)
