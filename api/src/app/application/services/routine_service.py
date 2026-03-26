from uuid import UUID

from app.application.dto.exercise import ExerciseDTO, ExerciseMuscleGroupDTO, MuscleGroupDTO
from app.application.dto.pagination import PaginationInput
from app.application.dto.routine import (
    AddRoutineExerciseInput,
    AddRoutineSetInput,
    CreateRoutineInput,
    PaginatedRoutines,
    RoutineDTO,
    RoutineExerciseDTO,
    RoutineSetDTO,
    UpdateRoutineExerciseInput,
    UpdateRoutineInput,
    UpdateRoutineSetInput,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.exceptions import EntityNotFoundException


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
            total = await self.uow.routine_repository.count()
            return PaginatedRoutines(
                items=[self._map_to_dto(r) for r in routines],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
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

    async def add_exercise(self, routine_id: UUID, input: AddRoutineExerciseInput) -> RoutineDTO:
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
                notes=input.notes,
            )
            # Use UUID for temporary IDs to ensure they are unique and can be tracked
            import uuid

            routine_set = RoutineSet(id=uuid.uuid4(), set_number=1, target_reps_max=10)
            routine_exercise.sets = [routine_set]
            routine.exercises.append(routine_exercise)

            await self.uow.routine_repository.update(routine)
            await self.uow.commit()
            return self._map_to_dto(routine)

    async def update_exercise(
        self, id: UUID, input: UpdateRoutineExerciseInput
    ) -> RoutineExerciseDTO:
        async with self.uow:
            re = await self.uow.routine_repository.get_exercise_by_id(id)
            if not re:
                raise EntityNotFoundException("RoutineExercise", id)

            if input.order is not None:
                re.order = input.order
            if input.superset_group is not None:
                re.superset_group = input.superset_group
            if input.rest_seconds is not None:
                re.rest_seconds = input.rest_seconds
            if input.notes is not None:
                re.notes = input.notes

            # Find the routine that owns this exercise
            routine = await self.uow.routine_repository.get_by_id(re.routine_id)  # type: ignore
            if routine:
                # Update the exercise in the routine list
                for i, ex in enumerate(routine.exercises):
                    if ex.id == re.id:
                        routine.exercises[i] = re
                        break
                await self.uow.routine_repository.update(routine)

            await self.uow.commit()
            return self._map_re_to_dto(re)

    async def remove_exercise(self, id: UUID) -> bool:
        async with self.uow:
            success = await self.uow.routine_repository.delete_exercise(id)
            if not success:
                raise EntityNotFoundException("RoutineExercise", id)
            await self.uow.commit()
            return True

    async def add_set(
        self, routine_exercise_id: UUID, input: AddRoutineSetInput
    ) -> RoutineExerciseDTO:
        async with self.uow:
            re = await self.uow.routine_repository.get_exercise_by_id(routine_exercise_id)
            if not re:
                raise EntityNotFoundException("RoutineExercise", routine_exercise_id)

            # Business Rule: Add a new set. If a set with the same set_number exists,
            # update it (upsert behavior). This allows users to modify existing sets
            # when planning routines.
            existing_set = next((s for s in re.sets if s.set_number == input.set_number), None)
            if existing_set:
                # Update the existing set with new values (upsert behavior)
                existing_set.set_type = input.set_type
                existing_set.target_reps_min = input.target_reps_min
                existing_set.target_reps_max = input.target_reps_max
                existing_set.target_rir = input.target_rir
                existing_set.target_weight_kg = input.target_weight_kg
                existing_set.weight_reduction_pct = input.weight_reduction_pct
                existing_set.rest_seconds = input.rest_seconds
            else:
                rs = RoutineSet(
                    set_number=input.set_number,
                    set_type=input.set_type,
                    target_reps_min=input.target_reps_min,
                    target_reps_max=input.target_reps_max,
                    target_rir=input.target_rir,
                    target_weight_kg=input.target_weight_kg,
                    weight_reduction_pct=input.weight_reduction_pct,
                    rest_seconds=input.rest_seconds,
                )
                re.sets.append(rs)

            # Find and update routine
            routine = await self.uow.routine_repository.get_by_id(re.routine_id)  # type: ignore
            if routine:
                for i, ex in enumerate(routine.exercises):
                    if ex.id == re.id:
                        routine.exercises[i] = re
                        break
                await self.uow.routine_repository.update(routine)

            await self.uow.commit()
            return self._map_re_to_dto(re)

    async def update_set(self, id: UUID, input: UpdateRoutineSetInput) -> RoutineSetDTO:
        async with self.uow:
            rs = await self.uow.routine_repository.get_set_by_id(id)
            if not rs:
                raise EntityNotFoundException("RoutineSet", id)

            if input.set_number is not None:
                rs.set_number = input.set_number
            if input.set_type is not None:
                rs.set_type = input.set_type
            if input.target_reps_min is not None:
                rs.target_reps_min = input.target_reps_min
            if input.target_reps_max is not None:
                rs.target_reps_max = input.target_reps_max
            if input.target_rir is not None:
                rs.target_rir = input.target_rir
            if input.target_weight_kg is not None:
                rs.target_weight_kg = input.target_weight_kg
            if input.weight_reduction_pct is not None:
                rs.weight_reduction_pct = input.weight_reduction_pct
            if input.rest_seconds is not None:
                rs.rest_seconds = input.rest_seconds

            # Update the owning routine exercise/routine
            re = await self.uow.routine_repository.get_exercise_by_id(rs.routine_exercise_id)  # type: ignore
            if re:
                for i, s in enumerate(re.sets):
                    if s.id == rs.id:
                        re.sets[i] = rs
                        break
                routine = await self.uow.routine_repository.get_by_id(re.routine_id)  # type: ignore
                if routine:
                    for i, ex in enumerate(routine.exercises):
                        if ex.id == re.id:
                            routine.exercises[i] = re
                            break
                    await self.uow.routine_repository.update(routine)

            await self.uow.commit()
            return self._map_set_to_dto(rs)

    async def remove_set(self, id: UUID) -> bool:
        async with self.uow:
            success = await self.uow.routine_repository.delete_set(id)
            if not success:
                raise EntityNotFoundException("RoutineSet", id)
            await self.uow.commit()
            return True

    def _map_re_to_dto(self, re: RoutineExercise) -> RoutineExerciseDTO:
        return RoutineExerciseDTO(
            id=re.id,
            exercise=ExerciseDTO(
                id=re.exercise.id,
                name=re.exercise.name,
                description=re.exercise.description,
                equipment=re.exercise.equipment,
                muscle_groups=[
                    ExerciseMuscleGroupDTO(
                        muscle_group=MuscleGroupDTO(
                            id=mg.muscle_group.id, name=mg.muscle_group.name
                        ),
                        role=mg.role,
                    )
                    for mg in re.exercise.muscle_groups
                ],
            ),
            order=re.order,
            superset_group=re.superset_group,
            rest_seconds=re.rest_seconds,
            notes=re.notes,
            sets=[self._map_set_to_dto(s) for s in re.sets],
        )

    def _map_set_to_dto(self, rs: RoutineSet) -> RoutineSetDTO:
        return RoutineSetDTO(
            id=rs.id,
            set_number=rs.set_number,
            set_type=rs.set_type,
            target_reps_min=rs.target_reps_min,
            target_reps_max=rs.target_reps_max,
            target_rir=rs.target_rir,
            target_weight_kg=rs.target_weight_kg,
            weight_reduction_pct=rs.weight_reduction_pct,
            rest_seconds=rs.rest_seconds,
        )

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
                                muscle_group=MuscleGroupDTO(
                                    id=mg.muscle_group.id, name=mg.muscle_group.name
                                ),
                                role=mg.role,
                            )
                            for mg in re.exercise.muscle_groups
                        ],
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
                            rest_seconds=rs.rest_seconds,
                        )
                        for rs in re.sets
                    ],
                )
                for re in routine.exercises
            ],
        )
