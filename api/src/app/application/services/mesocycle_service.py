from uuid import UUID
from datetime import date
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.dto.mesocycle import (
    MesocycleDTO,
    MesocycleWeekDTO,
    PlannedSessionDTO,
    CreateMesocycleInput,
    UpdateMesocycleInput,
    AddMesocycleWeekInput,
    UpdateMesocycleWeekInput,
    AddPlannedSessionInput,
    UpdatePlannedSessionInput,
    PaginatedMesocycles,
)
from app.application.dto.routine import RoutineDTO, RoutineExerciseDTO, RoutineSetDTO
from app.application.dto.exercise import ExerciseDTO, MuscleGroupDTO, ExerciseMuscleGroupDTO
from app.application.dto.pagination import PaginationInput
from app.domain.entities.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.domain.exceptions import EntityNotFoundException, ConflictException

class MesocycleService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_mesocycle(self, id: UUID) -> MesocycleDTO:
        async with self.uow:
            mesocycle = await self.uow.mesocycle_repository.get_by_id(id)
            if not mesocycle:
                raise EntityNotFoundException("Mesocycle", id)
            return self._map_to_dto(mesocycle)

    async def list_mesocycles(self, pagination: PaginationInput) -> PaginatedMesocycles:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            mesos = await self.uow.mesocycle_repository.list(offset=offset, limit=limit)
            total = 100 # In a real app, this would be a separate count query
            return PaginatedMesocycles(
                items=[self._map_to_dto(m) for m in mesos],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size
            )

    async def create_mesocycle(self, input: CreateMesocycleInput) -> MesocycleDTO:
        async with self.uow:
            meso = Mesocycle(
                name=input.name,
                description=input.description,
                start_date=input.start_date
            )
            await self.uow.mesocycle_repository.add(meso)
            await self.uow.commit()
            return self._map_to_dto(meso)

    async def update_mesocycle(self, id: UUID, input: UpdateMesocycleInput) -> MesocycleDTO:
        async with self.uow:
            meso = await self.uow.mesocycle_repository.get_by_id(id)
            if not meso:
                raise EntityNotFoundException("Mesocycle", id)
            
            if input.name is not None:
                meso.name = input.name
            if input.description is not None:
                meso.description = input.description
            if input.start_date is not None:
                meso.start_date = input.start_date
            if input.end_date is not None:
                meso.end_date = input.end_date
            if input.status is not None:
                meso.status = input.status
                
            await self.uow.mesocycle_repository.update(meso)
            await self.uow.commit()
            return self._map_to_dto(meso)

    async def delete_mesocycle(self, id: UUID) -> bool:
        async with self.uow:
            success = await self.uow.mesocycle_repository.delete(id)
            if not success:
                raise EntityNotFoundException("Mesocycle", id)
            await self.uow.commit()
            return True

    def _map_to_dto(self, meso: Mesocycle) -> MesocycleDTO:
        return MesocycleDTO(
            id=meso.id,
            name=meso.name,
            description=meso.description,
            start_date=meso.start_date,
            end_date=meso.end_date,
            status=meso.status,
            weeks=[
                MesocycleWeekDTO(
                    id=week.id,
                    week_number=week.week_number,
                    week_type=week.week_type,
                    start_date=week.start_date,
                    end_date=week.end_date,
                    planned_sessions=[
                        PlannedSessionDTO(
                            id=ps.id,
                            routine=self._map_routine_to_dto(ps.routine) if ps.routine else None,
                            day_of_week=ps.day_of_week,
                            date=ps.date,
                            notes=ps.notes
                        ) for ps in week.planned_sessions
                    ]
                ) for week in meso.weeks
            ]
        )

    def _map_routine_to_dto(self, routine) -> RoutineDTO:
        # Simplified for mapping within mesocycle
        return RoutineDTO(
            id=routine.id,
            name=routine.name,
            description=routine.description,
            exercises=[]
        )
