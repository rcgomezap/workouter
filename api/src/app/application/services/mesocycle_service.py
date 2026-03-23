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
from app.domain.enums import MesocycleStatus, WeekType
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

    async def list_mesocycles(
        self, pagination: PaginationInput, status: MesocycleStatus | None = None
    ) -> PaginatedMesocycles:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            if status:
                mesos = await self.uow.mesocycle_repository.list_by_status(
                    status, offset=offset, limit=limit
                )
                total = await self.uow.mesocycle_repository.count_by_status(status)
            else:
                mesos = await self.uow.mesocycle_repository.list(offset=offset, limit=limit)
                total = await self.uow.mesocycle_repository.count_total()

            return PaginatedMesocycles(
                items=[self._map_to_dto(m) for m in mesos],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

    async def create_mesocycle(self, input: CreateMesocycleInput) -> MesocycleDTO:
        async with self.uow:
            meso = Mesocycle(
                name=input.name, description=input.description, start_date=input.start_date
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

    async def add_week(self, mesocycle_id: UUID, input: AddMesocycleWeekInput) -> MesocycleWeekDTO:
        async with self.uow:
            meso = await self.uow.mesocycle_repository.get_by_id(mesocycle_id)
            if not meso:
                raise EntityNotFoundException("Mesocycle", mesocycle_id)

            week = MesocycleWeek(
                week_number=input.week_number,
                week_type=input.week_type,
                start_date=input.start_date,
                end_date=input.end_date,
            )
            # Use SQLAlchemy style if we are in repo context, but this is domain entity
            # Repo.update should handle the relationship if it's set up correctly
            # But usually we'd want a separate repo add for the week if it's top level.
            # Here it's nested.
            meso.weeks.append(week)
            await self.uow.mesocycle_repository.update(meso)
            await self.uow.commit()
            return self._map_week_to_dto(week)

    async def add_planned_session(
        self, mesocycle_week_id: UUID, input: AddPlannedSessionInput
    ) -> PlannedSessionDTO:
        async with self.uow:
            # We need to find the week. This might require a week repository or
            # navigating from a meso. For simplicity, assume we can get meso by week_id if repo supports it,
            # but usually repo get_by_id for week is cleaner.
            # Let's check what repositories we have.
            week = await self.uow.mesocycle_repository.get_week_by_id(mesocycle_week_id)
            if not week:
                raise EntityNotFoundException("MesocycleWeek", mesocycle_week_id)

            routine = None
            if input.routine_id:
                routine = await self.uow.routine_repository.get_by_id(input.routine_id)
                if not routine:
                    raise EntityNotFoundException("Routine", input.routine_id)

            ps = PlannedSession(
                mesocycle_week_id=mesocycle_week_id,
                routine=routine,
                day_of_week=input.day_of_week,
                date=input.date or date.today(),  # Fallback
                notes=input.notes,
            )
            week.planned_sessions.append(ps)
            # Update meso (owner of the week)
            # This depends on how the repo handles nested updates.
            # Assuming update on meso works if we have the meso.
            # For now, let's just try to update via meso repo if it can find meso by week.
            # Get the week again to ensure we have the mesocycle_id if not present
            # but week.mesocycle_id should be there.
            meso = await self.uow.mesocycle_repository.get_by_id(week.mesocycle_id)  # type: ignore
            print(f"DEBUG: Fetched meso={meso.id if meso else 'NONE'} for week synchronization")
            if meso:
                # IMPORTANT: We need to ensure the week we updated is the one in meso.weeks
                for i, w in enumerate(meso.weeks):
                    if w.id == week.id:
                        print(
                            f"DEBUG: Found week in meso.weeks, sessions count: {len(w.planned_sessions)}"
                        )
                        meso.weeks[i] = week
                        break
                await self.uow.mesocycle_repository.update(meso)
            await self.uow.commit()
            return self._map_planned_session_to_dto(ps)

    def _map_week_to_dto(self, week: MesocycleWeek) -> MesocycleWeekDTO:
        return MesocycleWeekDTO(
            id=week.id,
            week_number=week.week_number,
            week_type=week.week_type,
            start_date=week.start_date,
            end_date=week.end_date,
            planned_sessions=[self._map_planned_session_to_dto(ps) for ps in week.planned_sessions],
        )

    def _map_planned_session_to_dto(self, ps: PlannedSession) -> PlannedSessionDTO:
        return PlannedSessionDTO(
            id=ps.id,
            routine=self._map_routine_to_dto(ps.routine) if ps.routine else None,
            day_of_week=ps.day_of_week,
            date=ps.date,
            notes=ps.notes,
        )

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
                            notes=ps.notes,
                        )
                        for ps in week.planned_sessions
                    ],
                )
                for week in meso.weeks
            ],
        )

    def _map_routine_to_dto(self, routine) -> RoutineDTO:
        # Map full routine including exercises and sets
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
