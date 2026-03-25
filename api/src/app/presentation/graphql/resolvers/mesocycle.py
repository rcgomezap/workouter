import strawberry
from uuid import UUID
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.mesocycle import (
    Mesocycle,
    MesocycleWeek,
    PlannedSession,
    PaginatedMesocycles,
)
from app.presentation.graphql.types.enums import MesocycleStatus
from app.presentation.graphql.inputs.pagination import PaginationInput
from app.application.dto.pagination import PaginationInput as PaginationDTO
from app.domain.enums import MesocycleStatus as DomainMesocycleStatus
from app.presentation.graphql.resolvers.routine import map_routine


def map_planned_session(ps) -> PlannedSession:
    return PlannedSession(
        id=ps.id,
        routine=map_routine(ps.routine) if ps.routine else None,
        day_of_week=ps.day_of_week,
        date=ps.date,
        notes=ps.notes,
    )


def map_mesocycle_week(w) -> MesocycleWeek:
    return MesocycleWeek(
        id=w.id,
        week_number=w.week_number,
        week_type=w.week_type,
        start_date=w.start_date,
        end_date=w.end_date,
        planned_sessions=[map_planned_session(ps) for ps in w.planned_sessions],
    )


def map_mesocycle(m) -> Mesocycle:
    return Mesocycle(
        id=m.id,
        name=m.name,
        description=m.description,
        start_date=m.start_date,
        end_date=m.end_date,
        status=m.status,
        weeks=[map_mesocycle_week(w) for w in m.weeks],
    )


@strawberry.type
class MesocycleQuery:
    @strawberry.field
    async def mesocycles(
        self,
        info: Info[Context, None],
        pagination: PaginationInput | None = None,
        status: MesocycleStatus | None = None,
    ) -> PaginatedMesocycles:
        p_dto = PaginationDTO(
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else 20,
        )
        domain_status = DomainMesocycleStatus(status.value) if status else None
        result = await info.context.mesocycle_service.list_mesocycles(p_dto, domain_status)
        return PaginatedMesocycles(
            items=[map_mesocycle(m) for m in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
        )

    @strawberry.field
    async def mesocycle(self, info: Info[Context, None], id: UUID) -> Mesocycle:
        m = await info.context.mesocycle_service.get_mesocycle(id)
        return map_mesocycle(m)
