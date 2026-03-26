from uuid import UUID

import strawberry
from strawberry.types import Info

from app.application.dto.session import (
    AddSessionExerciseInput as AddSessionExerciseDTO,
)
from app.application.dto.session import (
    AddSessionSetInput as AddSessionSetDTO,
)
from app.application.dto.session import (
    CreateSessionInput as CreateSessionDTO,
)
from app.application.dto.session import (
    LogSetResultInput as LogSetResultDTO,
)
from app.application.dto.session import (
    UpdateSessionExerciseInput as UpdateSessionExerciseDTO,
)
from app.application.dto.session import (
    UpdateSessionInput as UpdateSessionDTO,
)
from app.application.dto.session import (
    UpdateSessionSetInput as UpdateSessionSetDTO,
)
from app.domain.enums import SessionStatus as DomainSessionStatus
from app.domain.enums import SetType as DomainSetType
from app.presentation.graphql.context import Context
from app.presentation.graphql.inputs.session import (
    AddSessionExerciseInput,
    AddSessionSetInput,
    CreateSessionInput,
    LogSetResultInput,
    UpdateSessionExerciseInput,
    UpdateSessionInput,
    UpdateSessionSetInput,
)
from app.presentation.graphql.types.exercise import Exercise
from app.presentation.graphql.types.session import Session, SessionExercise, SessionSet


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
        exercise=Exercise(
            id=se.exercise.id,
            name=se.exercise.name,
            description=se.exercise.description,
            equipment=se.exercise.equipment,
            muscle_groups=[],
        ),
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
class SessionMutation:
    @strawberry.mutation
    async def create_session(self, info: Info[Context, None], input: CreateSessionInput) -> Session:
        dto = CreateSessionDTO(
            planned_session_id=input.planned_session_id,
            mesocycle_id=input.mesocycle_id,
            routine_id=input.routine_id,
            notes=input.notes,
        )
        s = await info.context.session_service.create_session(dto)
        return map_session(s)

    @strawberry.mutation
    async def start_session(self, info: Info[Context, None], id: UUID) -> Session:
        s = await info.context.session_service.start_session(id)
        return map_session(s)

    @strawberry.mutation
    async def complete_session(self, info: Info[Context, None], id: UUID) -> Session:
        s = await info.context.session_service.complete_session(id)
        return map_session(s)

    @strawberry.mutation
    async def update_session(
        self, info: Info[Context, None], id: UUID, input: UpdateSessionInput
    ) -> Session:
        dto = UpdateSessionDTO(
            started_at=input.started_at,
            completed_at=input.completed_at,
            status=DomainSessionStatus(input.status.value) if input.status else None,
            notes=input.notes,
        )
        s = await info.context.session_service.update_session(id, dto)
        return map_session(s)

    @strawberry.mutation
    async def delete_session(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.session_service.delete_session(id)

    @strawberry.mutation
    async def add_session_exercise(
        self, info: Info[Context, None], session_id: UUID, input: AddSessionExerciseInput
    ) -> Session:
        dto = AddSessionExerciseDTO(
            exercise_id=input.exercise_id,
            order=input.order,
            superset_group=input.superset_group,
            rest_seconds=input.rest_seconds,
            notes=input.notes,
        )
        s = await info.context.session_service.add_exercise(session_id, dto)
        return map_session(s)

    @strawberry.mutation
    async def update_session_exercise(
        self, info: Info[Context, None], id: UUID, input: UpdateSessionExerciseInput
    ) -> SessionExercise:
        dto = UpdateSessionExerciseDTO(
            order=input.order,
            superset_group=input.superset_group,
            rest_seconds=input.rest_seconds,
            notes=input.notes,
        )
        se = await info.context.session_service.update_exercise(id, dto)
        return map_session_exercise(se)

    @strawberry.mutation
    async def remove_session_exercise(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.session_service.remove_exercise(id)

    @strawberry.mutation
    async def add_session_set(
        self, info: Info[Context, None], session_exercise_id: UUID, input: AddSessionSetInput
    ) -> SessionExercise:
        dto = AddSessionSetDTO(
            set_number=input.set_number,
            set_type=DomainSetType(input.set_type.value),
            target_reps=input.target_reps,
            target_rir=input.target_rir,
            target_weight_kg=input.target_weight_kg,
            weight_reduction_pct=input.weight_reduction_pct,
            rest_seconds=input.rest_seconds,
        )
        se = await info.context.session_service.add_set(session_exercise_id, dto)
        return map_session_exercise(se)

    @strawberry.mutation
    async def update_session_set(
        self, info: Info[Context, None], id: UUID, input: UpdateSessionSetInput
    ) -> SessionSet:
        dto = UpdateSessionSetDTO(
            set_number=input.set_number,
            set_type=DomainSetType(input.set_type.value) if input.set_type else None,
            target_reps=input.target_reps,
            target_rir=input.target_rir,
            target_weight_kg=input.target_weight_kg,
            weight_reduction_pct=input.weight_reduction_pct,
            rest_seconds=input.rest_seconds,
        )
        sset = await info.context.session_service.update_set(id, dto)
        return map_session_set(sset)

    @strawberry.mutation
    async def remove_session_set(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.session_service.remove_set(id)

    @strawberry.mutation
    async def log_set_result(
        self, info: Info[Context, None], set_id: UUID, input: LogSetResultInput
    ) -> SessionSet:
        dto = LogSetResultDTO(
            actual_reps=input.actual_reps,
            actual_rir=input.actual_rir,
            actual_weight_kg=input.actual_weight_kg,
            performed_at=input.performed_at,
        )
        sset = await info.context.session_service.log_set_result(set_id, dto)
        return map_session_set(sset)
