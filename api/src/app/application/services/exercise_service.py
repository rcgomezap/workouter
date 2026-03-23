from uuid import UUID
from typing import Sequence
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.dto.exercise import (
    ExerciseDTO,
    CreateExerciseInput,
    UpdateExerciseInput,
    MuscleGroupDTO,
    ExerciseMuscleGroupDTO,
    MuscleGroupAssignmentInput,
    PaginatedExercises,
)
from app.application.dto.pagination import PaginationInput
from app.domain.entities.exercise import Exercise, ExerciseMuscleGroup
from app.domain.exceptions import EntityNotFoundException, ConflictException

class ExerciseService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_exercise(self, id: UUID) -> ExerciseDTO:
        async with self.uow:
            exercise = await self.uow.exercise_repository.get_by_id(id)
            if not exercise:
                raise EntityNotFoundException("Exercise", id)
            return self._map_to_dto(exercise)

    async def list_exercises(
        self, pagination: PaginationInput, muscle_group_id: UUID | None = None
    ) -> PaginatedExercises:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            
            # This is a bit simplified, usually the repository would handle the filtering
            exercises = await self.uow.exercise_repository.list(offset=offset, limit=limit)
            total = 100 # In a real app, this would be a separate count query
            
            return PaginatedExercises(
                items=[self._map_to_dto(e) for e in exercises],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size
            )

    async def create_exercise(self, input: CreateExerciseInput) -> ExerciseDTO:
        async with self.uow:
            exercise = Exercise(
                name=input.name,
                description=input.description,
                equipment=input.equipment
            )
            await self.uow.exercise_repository.add(exercise)
            await self.uow.commit()
            return self._map_to_dto(exercise)

    async def update_exercise(self, id: UUID, input: UpdateExerciseInput) -> ExerciseDTO:
        async with self.uow:
            exercise = await self.uow.exercise_repository.get_by_id(id)
            if not exercise:
                raise EntityNotFoundException("Exercise", id)
            
            if input.name is not None:
                exercise.name = input.name
            if input.description is not None:
                exercise.description = input.description
            if input.equipment is not None:
                exercise.equipment = input.equipment
                
            await self.uow.exercise_repository.update(exercise)
            await self.uow.commit()
            return self._map_to_dto(exercise)

    async def delete_exercise(self, id: UUID) -> bool:
        async with self.uow:
            # Business Rule: Check if referenced by routines or sessions
            # This would typically be checked by the repository or DB constraints
            # but we can do a quick check here if needed.
            success = await self.uow.exercise_repository.delete(id)
            if not success:
                 raise EntityNotFoundException("Exercise", id)
            await self.uow.commit()
            return True

    async def assign_muscle_groups(
        self, exercise_id: UUID, assignments: list[MuscleGroupAssignmentInput]
    ) -> ExerciseDTO:
        async with self.uow:
            exercise = await self.uow.exercise_repository.get_by_id(exercise_id)
            if not exercise:
                raise EntityNotFoundException("Exercise", exercise_id)
            
            new_muscle_groups = []
            for assign in assignments:
                mg = await self.uow.muscle_group_repository.get_by_id(assign.muscle_group_id)
                if not mg:
                    raise EntityNotFoundException("MuscleGroup", assign.muscle_group_id)
                new_muscle_groups.append(ExerciseMuscleGroup(muscle_group=mg, role=assign.role))
            
            exercise.muscle_groups = new_muscle_groups
            await self.uow.exercise_repository.update(exercise)
            await self.uow.commit()
            return self._map_to_dto(exercise)

    def _map_to_dto(self, exercise: Exercise) -> ExerciseDTO:
        return ExerciseDTO(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            equipment=exercise.equipment,
            muscle_groups=[
                ExerciseMuscleGroupDTO(
                    muscle_group=MuscleGroupDTO(id=mg.muscle_group.id, name=mg.muscle_group.name),
                    role=mg.role
                ) for mg in exercise.muscle_groups
            ]
        )
