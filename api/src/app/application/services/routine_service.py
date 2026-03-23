from uuid import UUID
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.dto.routine import (
    RoutineDTO,
    RoutineExerciseDTO,
    RoutineSetDTO,
    CreateRoutineInput,
    UpdateRoutineInput,
    AddRoutineExerciseInput,
    UpdateRoutineExerciseInput,
    AddRoutineSetInput,
    UpdateRoutineSetInput,
    PaginatedRoutines,
)
from app.application.dto.exercise import ExerciseDTO, MuscleGroupDTO, ExerciseMuscleGroupDTO
from app.application.dto.pagination import PaginationInput
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.exceptions import EntityNotFoundException, ConflictException

class RoutineService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_routine(self, id: UUID) -> RoutineDTO:
        async with self.uow:
            routine = await self.uow.routine_repository.get_by_id(id)
            if not routine:
                raise EntityNotFoundException("Routine", id)
            return self._map_to_dto(routine)

    async def list_routines(self, pagination: PaginationInput) -> PaginatedRoutines:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            routines = await self.uow.routine_repository.list(offset=offset, limit=limit)
            total = 100 # In a real app, this would be a separate count query
            return PaginatedRoutines(
                items=[self._map_to_dto(r) for r in routines],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size
            )

    async def create_routine(self, input: CreateRoutineInput) -> RoutineDTO:
        async with self.uow:
            routine = Routine(name=input.name, description=input.description)
            await self.uow.routine_repository.add(routine)
            await self.uow.commit()
            return self._map_to_dto(routine)

    async def update_routine(self, id: UUID, input: UpdateRoutineInput) -> RoutineDTO:
        async with self.uow:
            routine = await self.uow.routine_repository.get_by_id(id)
            if not routine:
                raise EntityNotFoundException("Routine", id)
            if input.name is not None:
                routine.name = input.name
            if input.description is not None:
                routine.description = input.description
            await self.uow.routine_repository.update(routine)
            await self.uow.commit()
            return self._map_to_dto(routine)

    async def delete_routine(self, id: UUID) -> bool:
        async with self.uow:
            # Business Rule: Block if referenced by planned_session or session
            # This should be handled by repository or DB constraints
            success = await self.uow.routine_repository.delete(id)
            if not success:
                raise EntityNotFoundException("Routine", id)
            await self.uow.commit()
            return True

    async def add_routine_exercise(self, routine_id: UUID, input: AddRoutineExerciseInput) -> RoutineDTO:
        async with self.uow:
            routine = await self.uow.routine_repository.get_by_id(routine_id)
            if not routine:
                raise EntityNotFoundException("Routine", routine_id)
            exercise = await self.uow.exercise_repository.get_by_id(input.exercise_id)
            if not exercise:
                raise EntityNotFoundException("Exercise", input.exercise_id)
            
            routine_exercise = RoutineExercise(
                exercise=exercise,
                order=input.order,
                superset_group=input.superset_group,
                rest_seconds=input.rest_seconds,
                notes=input.notes
            )
            routine.exercises.append(routine_exercise)
            await self.uow.routine_repository.update(routine)
            await self.uow.commit()
            return self._map_to_dto(routine)

    # ... Other methods for updateRoutineExercise, addRoutineSet, etc. ...

    def _map_to_dto(self, routine: Routine) -> RoutineDTO:
        return RoutineDTO(
            id=routine.id,
            name=routine.name,
            description=routine.description,
            exercises=[
                RoutineExerciseDTO(
                    id=re.id,
                    exercise=ExerciseDTO(
                        id=re.exercise.id,
                        name=re.exercise.name,
                        description=re.exercise.description,
                        equipment=re.exercise.equipment,
                        muscle_groups=[
                            ExerciseMuscleGroupDTO(
                                muscle_group=MuscleGroupDTO(id=mg.muscle_group.id, name=mg.muscle_group.name),
                                role=mg.role
                            ) for mg in re.exercise.muscle_groups
                        ]
                    ),
                    order=re.order,
                    superset_group=re.superset_group,
                    rest_seconds=re.rest_seconds,
                    notes=re.notes,
                    sets=[
                        RoutineSetDTO(
                            id=rs.id,
                            set_number=rs.set_number,
                            set_type=rs.set_type,
                            target_reps_min=rs.target_reps_min,
                            target_reps_max=rs.target_reps_max,
                            target_rir=rs.target_rir,
                            target_weight_kg=rs.target_weight_kg,
                            weight_reduction_pct=rs.weight_reduction_pct,
                            rest_seconds=rs.rest_seconds
                        ) for rs in re.sets
                    ]
                ) for re in routine.exercises
            ]
        )
