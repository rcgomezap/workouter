import strawberry
from uuid import UUID
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.routine import Routine, RoutineExercise, RoutineSet
from app.presentation.graphql.types.exercise import Exercise
from app.presentation.graphql.inputs.routine import (
    CreateRoutineInput,
    UpdateRoutineInput,
    AddRoutineExerciseInput,
    UpdateRoutineExerciseInput,
    AddRoutineSetInput,
    UpdateRoutineSetInput,
)
from app.application.dto.routine import (
    CreateRoutineInput as CreateRoutineDTO,
    UpdateRoutineInput as UpdateRoutineDTO,
    AddRoutineExerciseInput as AddRoutineExerciseDTO,
    UpdateRoutineExerciseInput as UpdateRoutineExerciseDTO,
    AddRoutineSetInput as AddRoutineSetDTO,
    UpdateRoutineSetInput as UpdateRoutineSetDTO,
)
from app.domain.enums import SetType as DomainSetType

def map_routine_set(s) -> RoutineSet:
    return RoutineSet(
        id=s.id,
        set_number=s.set_number,
        set_type=s.set_type,
        target_reps_min=s.target_reps_min,
        target_reps_max=s.target_reps_max,
        target_rir=s.target_rir,
        target_weight_kg=s.target_weight_kg,
        weight_reduction_pct=s.weight_reduction_pct,
        rest_seconds=s.rest_seconds
    )

def map_routine_exercise(re) -> RoutineExercise:
    return RoutineExercise(
        id=re.id,
        exercise=Exercise(
            id=re.exercise.id,
            name=re.exercise.name,
            description=re.exercise.description,
            equipment=re.exercise.equipment,
            muscle_groups=[]
        ),
        order=re.order,
        superset_group=re.superset_group,
        rest_seconds=re.rest_seconds,
        notes=re.notes,
        sets=[map_routine_set(s) for s in re.sets]
    )

def map_routine(r) -> Routine:
    return Routine(
        id=r.id,
        name=r.name,
        description=r.description,
        exercises=[map_routine_exercise(re) for re in r.exercises]
    )

@strawberry.type
class RoutineMutation:
    @strawberry.mutation
    async def create_routine(
        self, 
        info: Info[Context, None], 
        input: CreateRoutineInput
    ) -> Routine:
        dto = CreateRoutineDTO(name=input.name, description=input.description)
        r = await info.context.routine_service.create_routine(dto)
        return map_routine(r)

    @strawberry.mutation
    async def update_routine(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateRoutineInput
    ) -> Routine:
        dto = UpdateRoutineDTO(name=input.name, description=input.description)
        r = await info.context.routine_service.update_routine(id, dto)
        return map_routine(r)

    @strawberry.mutation
    async def delete_routine(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.routine_service.delete_routine(id)

    @strawberry.mutation
    async def add_routine_exercise(
        self, 
        info: Info[Context, None], 
        routine_id: UUID, 
        input: AddRoutineExerciseInput
    ) -> Routine:
        dto = AddRoutineExerciseDTO(
            exercise_id=input.exercise_id,
            order=input.order,
            superset_group=input.superset_group,
            rest_seconds=input.rest_seconds,
            notes=input.notes
        )
        r = await info.context.routine_service.add_exercise(routine_id, dto)
        return map_routine(r)

    @strawberry.mutation
    async def update_routine_exercise(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateRoutineExerciseInput
    ) -> RoutineExercise:
        dto = UpdateRoutineExerciseDTO(
            order=input.order,
            superset_group=input.superset_group,
            rest_seconds=input.rest_seconds,
            notes=input.notes
        )
        re = await info.context.routine_service.update_exercise(id, dto)
        return map_routine_exercise(re)

    @strawberry.mutation
    async def remove_routine_exercise(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.routine_service.remove_exercise(id)

    @strawberry.mutation
    async def add_routine_set(
        self, 
        info: Info[Context, None], 
        routine_exercise_id: UUID, 
        input: AddRoutineSetInput
    ) -> RoutineExercise:
        dto = AddRoutineSetDTO(
            set_number=input.set_number,
            set_type=DomainSetType(input.set_type.value),
            target_reps_min=input.target_reps_min,
            target_reps_max=input.target_reps_max,
            target_rir=input.target_rir,
            target_weight_kg=input.target_weight_kg,
            weight_reduction_pct=input.weight_reduction_pct,
            rest_seconds=input.rest_seconds
        )
        re = await info.context.routine_service.add_set(routine_exercise_id, dto)
        return map_routine_exercise(re)

    @strawberry.mutation
    async def update_routine_set(
        self, 
        info: Info[Context, None], 
        id: UUID, 
        input: UpdateRoutineSetInput
    ) -> RoutineSet:
        dto = UpdateRoutineSetDTO(
            set_number=input.set_number,
            set_type=DomainSetType(input.set_type.value) if input.set_type else None,
            target_reps_min=input.target_reps_min,
            target_reps_max=input.target_reps_max,
            target_rir=input.target_rir,
            target_weight_kg=input.target_weight_kg,
            weight_reduction_pct=input.weight_reduction_pct,
            rest_seconds=input.rest_seconds
        )
        s = await info.context.routine_service.update_set(id, dto)
        return map_routine_set(s)

    @strawberry.mutation
    async def remove_routine_set(self, info: Info[Context, None], id: UUID) -> bool:
        return await info.context.routine_service.remove_set(id)
