from uuid import UUID
from datetime import UTC, datetime
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.dto.session import (
    SessionDTO,
    SessionExerciseDTO,
    SessionSetDTO,
    CreateSessionInput,
    UpdateSessionInput,
    AddSessionExerciseInput,
    UpdateSessionExerciseInput,
    AddSessionSetInput,
    UpdateSessionSetInput,
    LogSetResultInput,
    PaginatedSessions,
)
from app.application.dto.exercise import ExerciseDTO, MuscleGroupDTO, ExerciseMuscleGroupDTO
from app.application.dto.pagination import PaginationInput
from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus
from app.domain.exceptions import EntityNotFoundException, ConflictException

class SessionService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_session(self, id: UUID) -> SessionDTO:
        async with self.uow:
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
            return self._map_to_dto(session)

    async def list_sessions(self, pagination: PaginationInput) -> PaginatedSessions:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            sessions = await self.uow.session_repository.list(offset=offset, limit=limit)
            total = 100 # In a real app, this would be a separate count query
            return PaginatedSessions(
                items=[self._map_to_dto(s) for s in sessions],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size
            )

    async def create_session(self, input: CreateSessionInput) -> SessionDTO:
        async with self.uow:
            session = Session(
                planned_session_id=input.planned_session_id,
                mesocycle_id=input.mesocycle_id,
                routine_id=input.routine_id,
                notes=input.notes,
                status=SessionStatus.PLANNED
            )
            
            # Business Rule 1: Session creation from routine
            if input.routine_id:
                routine = await self.uow.routine_repository.get_by_id(input.routine_id)
                if not routine:
                    raise EntityNotFoundException("Routine", input.routine_id)
                
                for re in routine.exercises:
                    session_exercise = SessionExercise(
                        exercise=re.exercise,
                        order=re.order,
                        superset_group=re.superset_group,
                        rest_seconds=re.rest_seconds,
                        notes=re.notes
                    )
                    for rs in re.sets:
                        session_set = SessionSet(
                            set_number=rs.set_number,
                            set_type=rs.set_type,
                            target_reps=rs.target_reps_max, # default to max target
                            target_rir=rs.target_rir,
                            target_weight_kg=rs.target_weight_kg,
                            weight_reduction_pct=rs.weight_reduction_pct,
                            rest_seconds=rs.rest_seconds
                        )
                        session_exercise.sets.append(session_set)
                    session.exercises.append(session_exercise)
            
            await self.uow.session_repository.add(session)
            await self.uow.commit()
            return self._map_to_dto(session)

    async def start_session(self, id: UUID) -> SessionDTO:
        async with self.uow:
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
            
            # Business Rule 3: Status transitions
            if session.status != SessionStatus.PLANNED:
                raise ConflictException(f"Cannot start session in status {session.status}")
                
            session.status = SessionStatus.IN_PROGRESS
            session.started_at = datetime.now(UTC)
            await self.uow.session_repository.update(session)
            await self.uow.commit()
            return self._map_to_dto(session)

    async def complete_session(self, id: UUID) -> SessionDTO:
        async with self.uow:
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
                
            if session.status != SessionStatus.IN_PROGRESS:
                raise ConflictException(f"Cannot complete session in status {session.status}")
                
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(UTC)
            await self.uow.session_repository.update(session)
            await self.uow.commit()
            return self._map_to_dto(session)

    async def log_set_result(self, set_id: UUID, input: LogSetResultInput) -> SessionSetDTO:
        async with self.uow:
            # Finding the set in repository by ID might be needed. 
            # Simplified here assuming session_repository can find sets.
            session_set = await self.uow.session_repository.get_set_by_id(set_id)
            if not session_set:
                raise EntityNotFoundException("SessionSet", set_id)
            
            session_set.actual_reps = input.actual_reps
            session_set.actual_rir = input.actual_rir
            session_set.actual_weight_kg = input.actual_weight_kg
            session_set.performed_at = input.performed_at or datetime.now(UTC)
            
            await self.uow.session_repository.update_set(session_set)
            await self.uow.commit()
            return self._map_set_to_dto(session_set)

    def _map_to_dto(self, session: Session) -> SessionDTO:
        return SessionDTO(
            id=session.id,
            planned_session_id=session.planned_session_id,
            mesocycle_id=session.mesocycle_id,
            routine_id=session.routine_id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            notes=session.notes,
            exercises=[
                SessionExerciseDTO(
                    id=se.id,
                    exercise=ExerciseDTO(
                        id=se.exercise.id,
                        name=se.exercise.name,
                        description=se.exercise.description,
                        equipment=se.exercise.equipment,
                        muscle_groups=[
                            ExerciseMuscleGroupDTO(
                                muscle_group=MuscleGroupDTO(id=mg.muscle_group.id, name=mg.muscle_group.name),
                                role=mg.role
                            ) for mg in se.exercise.muscle_groups
                        ]
                    ),
                    order=se.order,
                    superset_group=se.superset_group,
                    rest_seconds=se.rest_seconds,
                    notes=se.notes,
                    sets=[self._map_set_to_dto(ss) for ss in se.sets]
                ) for se in session.exercises
            ]
        )
    
    def _map_set_to_dto(self, ss: SessionSet) -> SessionSetDTO:
        return SessionSetDTO(
            id=ss.id,
            set_number=ss.set_number,
            set_type=ss.set_type,
            target_reps=ss.target_reps,
            target_rir=ss.target_rir,
            target_weight_kg=ss.target_weight_kg,
            actual_reps=ss.actual_reps,
            actual_rir=ss.actual_rir,
            actual_weight_kg=ss.actual_weight_kg,
            weight_reduction_pct=ss.weight_reduction_pct,
            rest_seconds=ss.rest_seconds,
            performed_at=ss.performed_at
        )
