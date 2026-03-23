import strawberry
from uuid import UUID
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.presentation.graphql.types.routine import Routine
from app.presentation.graphql.inputs.mesocycle import (
    CreateMesocycleInput,
    UpdateMesocycleInput,
    AddMesocycleWeekInput,
    UpdateMesocycleWeekInput,
    AddPlannedSessionInput,
    UpdatePlannedSessionInput,
)
from app.application.dto.mesocycle import (
    CreateMesocycleInput as CreateMesocycleDTO,
    UpdateMesocycleInput as UpdateMesocycleDTO,
    AddMesocycleWeekInput as AddMesocycleWeekDTO,
    UpdateMesocycleWeekInput as UpdateMesocycleWeekDTO,
    AddPlannedSessionInput as AddPlannedSessionDTO,
    UpdatePlannedSessionInput as UpdatePlannedSessionDTO,
)
from app.domain.enums import (
    MesocycleStatus as DomainMesocycleStatus,
    WeekType as DomainWeekType
)

def map_planned_session(ps) -> PlannedSession:
    return PlannedSession(
        id=ps.id,
        routine=Routine(
            id=ps.routine.id,
            name=ps.routine.name,
            description=ps.routine.description,
            exercises=[]
        ) if ps.routine else None,
        day_of_week=ps.day_of_week,
        date=ps.date,
        notes=ps.notes
    )

def map_mesocycle_week(w) -> MesocycleWeek:
    return MesocycleWeek(
        id=w.id,
        week_number=w.week_number,
        week_type=w.week_type,
        start_date=w.start_date,
        end_date=w.end_date,
        planned_sessions=[map_planned_session(ps) for ps in w.planned_sessions]
    )

def map_mesocycle(m) -> Mesocycle:
    return Mesocycle(
        id=m.id,
        name=m.name,
        description=m.description,
        start_date=m.start_date,
        end_date=m.end_date,
        status=m.status,
        weeks=[map_mesocycle_week(w) for w in m.weeks]
    )

@strawberry.type
class MesocycleMutation:
    @strawberry.mutation
    async def create_mesocycle(
        self, 
        info: Info[Context, None], 
        input: CreateMesocycleInput
    ) -> Mesocycle:
        dto = CreateMesocycleDTO(
            name=input.name,
            description=input.description,
            start_date=input.start_date
        )
        m = await info.context.mesocycle_service.create_mesocycle(dto)
        return map_mesocycle(m)

    @strawberry.mutation
    async def update_mesocycle(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateMesocycleInput
    ) -> Mesocycle:
        dto = UpdateMesocycleDTO(
            name=input.name,
            description=input.description,
            start_date=input.start_date,
            end_date=input.end_date,
            status=DomainMesocycleStatus(input.status.value) if input.status else None
        )
        m = await info.context.mesocycle_service.update_mesocycle(id, dto)
        return map_mesocycle(m)

    @strawberry.mutation
    async def delete_mesocycle(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.mesocycle_service.delete_mesocycle(id)

    @strawberry.mutation
    async def add_mesocycle_week(
        self, 
        info: Info[Context, None], 
        mesocycle_id: UUID, 
        input: AddMesocycleWeekInput
    ) -> MesocycleWeek:
        dto = AddMesocycleWeekDTO(
            week_number=input.week_number,
            week_type=DomainWeekType(input.week_type.value),
            start_date=input.start_date,
            end_date=input.end_date
        )
        w = await info.context.mesocycle_service.add_week(mesocycle_id, dto)
        return map_mesocycle_week(w)

    @strawberry.mutation
    async def update_mesocycle_week(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateMesocycleWeekInput
    ) -> MesocycleWeek:
        dto = UpdateMesocycleWeekDTO(
            week_number=input.week_number,
            week_type=DomainWeekType(input.week_type.value) if input.week_type else None,
            start_date=input.start_date,
            end_date=input.end_date
        )
        w = await info.context.mesocycle_service.update_week(id, dto)
        return map_mesocycle_week(w)

    @strawberry.mutation
    async def remove_mesocycle_week(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.mesocycle_service.remove_week(id)

    @strawberry.mutation
    async def add_planned_session(
        self, 
        info: Info[Context, None], 
        mesocycle_week_id: UUID, 
        input: AddPlannedSessionInput
    ) -> PlannedSession:
        dto = AddPlannedSessionDTO(
            routine_id=input.routine_id,
            day_of_week=input.day_of_week,
            date=input.date,
            notes=input.notes
        )
        ps = await info.context.mesocycle_service.add_planned_session(mesocycle_week_id, dto)
        return map_planned_session(ps)

    @strawberry.mutation
    async def update_planned_session(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdatePlannedSessionInput
    ) -> PlannedSession:
        dto = UpdatePlannedSessionDTO(
            routine_id=input.routine_id,
            day_of_week=input.day_of_week,
            date=input.date,
            notes=input.notes
        )
        ps = await info.context.mesocycle_service.update_planned_session(id, dto)
        return map_planned_session(ps)

    @strawberry.mutation
    async def remove_planned_session(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.mesocycle_service.remove_planned_session(id)
