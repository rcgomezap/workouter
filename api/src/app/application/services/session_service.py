from datetime import UTC, date, datetime
from uuid import UUID

from app.application.dto.exercise import ExerciseDTO, ExerciseMuscleGroupDTO, MuscleGroupDTO
from app.application.dto.pagination import PaginationInput
from app.application.dto.session import (
    AddSessionExerciseInput,
    AddSessionSetInput,
    CreateSessionInput,
    LogSetResultInput,
    PaginatedSessions,
    SessionDTO,
    SessionExerciseDTO,
    SessionSetDTO,
    UpdateSessionExerciseInput,
    UpdateSessionSetInput,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus
from app.domain.exceptions import ConflictException, EntityNotFoundException


class SessionService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_session(self, id: UUID) -> SessionDTO:
        async with self.uow:
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
            return self._map_to_dto(session)

    async def list_sessions(
        self,
        pagination: PaginationInput,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> PaginatedSessions:
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            limit = pagination.page_size
            sessions = await self.uow.session_repository.list_by_filters(
                status=status,
                mesocycle_id=mesocycle_id,
                date_from=date_from,
                date_to=date_to,
                offset=offset,
                limit=limit,
            )
            total = await self.uow.session_repository.count_by_filters(
                status=status,
                mesocycle_id=mesocycle_id,
                date_from=date_from,
                date_to=date_to,
            )
            return PaginatedSessions(
                items=[self._map_to_dto(s) for s in sessions],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

    async def create_session(self, input: CreateSessionInput) -> SessionDTO:
        async with self.uow:
            print(f"DEBUG: Creating session for planned_session_id={input.planned_session_id}")
            session = Session(
                planned_session_id=input.planned_session_id,
                mesocycle_id=input.mesocycle_id,
                routine_id=input.routine_id,
                notes=input.notes,
                status=SessionStatus.PLANNED,
            )

            # Business Rule: Use routine from planned session if not provided
            routine_id = input.routine_id
            if not routine_id and input.planned_session_id:
                planned_session = await self.uow.mesocycle_repository.get_planned_session_by_id(
                    input.planned_session_id
                )
                print(f"DEBUG: Fetched planned_session={planned_session}")
                if planned_session:
                    if planned_session.routine:
                        routine_id = planned_session.routine.id
                        print(f"DEBUG: Found routine_id={routine_id} in planned_session")
                        session.routine_id = routine_id

                    # Ensure mesocycle_id is set from the week if missing
                    if not session.mesocycle_id:
                        week = await self.uow.mesocycle_repository.get_week_by_id(
                            planned_session.mesocycle_week_id
                        )
                        if week:
                            session.mesocycle_id = week.mesocycle_id
                            print(f"DEBUG: Found mesocycle_id={session.mesocycle_id} from week")

            # Business Rule 1: Session creation from routine
            if routine_id:
                # Fetch routine WITH exercises and sets
                routine = await self.uow.routine_repository.get_by_id(routine_id)
                print(f"DEBUG: Fetched routine={routine}")
                if not routine:
                    raise EntityNotFoundException("Routine", routine_id)

                print(f"DEBUG: Routine exercises count: {len(routine.exercises)}")
                for re in routine.exercises:
                    print(f"DEBUG: Cloning routine exercise {re.id}, sets count: {len(re.sets)}")
                    session_exercise = SessionExercise(
                        exercise=re.exercise,
                        order=re.order,
                        superset_group=re.superset_group,
                        rest_seconds=re.rest_seconds,
                        notes=re.notes,
                    )
                    # Initialize sets collection if it's not already
                    session_exercise.sets = []
                    for rs in re.sets:
                        print(f"DEBUG: Cloning routine set {rs.id}")
                        session_set = SessionSet(
                            set_number=rs.set_number,
                            set_type=rs.set_type,
                            target_reps=rs.target_reps_max,  # default to max target
                            target_rir=rs.target_rir,
                            target_weight_kg=rs.target_weight_kg,
                            weight_reduction_pct=rs.weight_reduction_pct,
                            rest_seconds=rs.rest_seconds,
                        )
                        session_exercise.sets.append(session_set)
                    session.exercises.append(session_exercise)

            await self.uow.session_repository.add(session)
            print(f"DEBUG: Added session to repository, exercises count: {len(session.exercises)}")
            # IMPORTANT: Flush before commit to populate generated IDs for nested objects
            await self.uow.flush()
            await self.uow.commit()

            # Re-fetch to ensure all nested data is loaded for DTO mapping
            # (session_repository.add might not return fully loaded relationships)
            full_session = await self.uow.session_repository.get_by_id(session.id)
            if not full_session:
                raise EntityNotFoundException("Session", session.id)
            print(f"DEBUG: Re-fetched full_session, exercises count: {len(full_session.exercises)}")
            return self._map_to_dto(full_session)

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

            # Re-fetch for DTO mapping
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
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

            # Re-fetch for DTO mapping
            session = await self.uow.session_repository.get_by_id(id)
            if not session:
                raise EntityNotFoundException("Session", id)
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

    async def add_exercise(self, session_id: UUID, input: AddSessionExerciseInput) -> SessionDTO:
        async with self.uow:
            session = await self.uow.session_repository.get_by_id(session_id)
            if not session:
                raise EntityNotFoundException("Session", session_id)

            exercise = await self.uow.exercise_repository.get_by_id(input.exercise_id)
            if not exercise:
                raise EntityNotFoundException("Exercise", input.exercise_id)

            session_exercise = SessionExercise(
                exercise=exercise,
                order=input.order,
                superset_group=input.superset_group,
                rest_seconds=input.rest_seconds,
                notes=input.notes,
                sets=[],
            )

            await self.uow.session_repository.add_exercise(session_id, session_exercise)
            await self.uow.commit()

            # Re-fetch session to include new exercise in the list
            session = await self.uow.session_repository.get_by_id(session_id)
            return self._map_to_dto(session)

    async def update_exercise(
        self, id: UUID, input: UpdateSessionExerciseInput
    ) -> SessionExerciseDTO:
        async with self.uow:
            session_exercise = await self.uow.session_repository.get_exercise_by_id(id)
            if not session_exercise:
                raise EntityNotFoundException("SessionExercise", id)

            if input.order is not None:
                session_exercise.order = input.order
            if input.superset_group is not None:
                session_exercise.superset_group = input.superset_group
            if input.rest_seconds is not None:
                session_exercise.rest_seconds = input.rest_seconds
            if input.notes is not None:
                session_exercise.notes = input.notes

            updated_se = await self.uow.session_repository.update_exercise(session_exercise)
            await self.uow.commit()

            # The repository method might not return fully loaded relationships needed for DTO
            # Safe to re-fetch or trust repository implementation
            # Given my repository implementation, it calls _to_exercise_domain but relies on loaded relationships.
            # Let's trust it returns a valid domain object.

            # However, we need to map to DTO. _map_to_dto handles full session.
            # We need a method to map single exercise.
            # _map_to_dto does it inline. I should extract _map_exercise_to_dto if possible,
            # or just copy the logic. I'll duplicate logic inside _map_to_dto for now to be safe and quick.

            return SessionExerciseDTO(
                id=updated_se.id,
                exercise=ExerciseDTO(
                    id=updated_se.exercise.id,
                    name=updated_se.exercise.name,
                    description=updated_se.exercise.description,
                    equipment=updated_se.exercise.equipment,
                    muscle_groups=[
                        ExerciseMuscleGroupDTO(
                            muscle_group=MuscleGroupDTO(
                                id=mg.muscle_group.id, name=mg.muscle_group.name
                            ),
                            role=mg.role,
                        )
                        for mg in updated_se.exercise.muscle_groups
                    ],
                ),
                order=updated_se.order,
                superset_group=updated_se.superset_group,
                rest_seconds=updated_se.rest_seconds,
                notes=updated_se.notes,
                sets=[self._map_set_to_dto(ss) for ss in updated_se.sets],
            )

    async def remove_exercise(self, id: UUID) -> bool:
        async with self.uow:
            # Check existence first? Or let repo handle it?
            # Repo returns None if not found, but delete returns None.
            # Better check.
            se = await self.uow.session_repository.get_exercise_by_id(id)
            if not se:
                raise EntityNotFoundException("SessionExercise", id)

            await self.uow.session_repository.delete_exercise(id)
            await self.uow.commit()
            return True

    async def add_set(
        self, session_exercise_id: UUID, input: AddSessionSetInput
    ) -> SessionExerciseDTO:
        async with self.uow:
            session_exercise = await self.uow.session_repository.get_exercise_by_id(
                session_exercise_id
            )
            if not session_exercise:
                raise EntityNotFoundException("SessionExercise", session_exercise_id)

            session_set = SessionSet(
                set_number=input.set_number,
                set_type=input.set_type,
                target_reps=input.target_reps,
                target_rir=input.target_rir,
                target_weight_kg=input.target_weight_kg,
                weight_reduction_pct=input.weight_reduction_pct,
                rest_seconds=input.rest_seconds,
            )

            await self.uow.session_repository.add_set(session_exercise_id, session_set)
            await self.uow.commit()

            # Re-fetch exercise to get updated list of sets
            session_exercise = await self.uow.session_repository.get_exercise_by_id(
                session_exercise_id
            )

            # Map to DTO
            return SessionExerciseDTO(
                id=session_exercise.id,
                exercise=ExerciseDTO(
                    id=session_exercise.exercise.id,
                    name=session_exercise.exercise.name,
                    description=session_exercise.exercise.description,
                    equipment=session_exercise.exercise.equipment,
                    muscle_groups=[
                        ExerciseMuscleGroupDTO(
                            muscle_group=MuscleGroupDTO(
                                id=mg.muscle_group.id, name=mg.muscle_group.name
                            ),
                            role=mg.role,
                        )
                        for mg in session_exercise.exercise.muscle_groups
                    ],
                ),
                order=session_exercise.order,
                superset_group=session_exercise.superset_group,
                rest_seconds=session_exercise.rest_seconds,
                notes=session_exercise.notes,
                sets=[self._map_set_to_dto(ss) for ss in session_exercise.sets],
            )

    async def update_set(self, id: UUID, input: UpdateSessionSetInput) -> SessionSetDTO:
        async with self.uow:
            session_set = await self.uow.session_repository.get_set_by_id(id)
            if not session_set:
                raise EntityNotFoundException("SessionSet", id)

            if input.set_number is not None:
                session_set.set_number = input.set_number
            if input.set_type is not None:
                session_set.set_type = input.set_type
            if input.target_reps is not None:
                session_set.target_reps = input.target_reps
            if input.target_rir is not None:
                session_set.target_rir = input.target_rir
            if input.target_weight_kg is not None:
                session_set.target_weight_kg = input.target_weight_kg
            if input.weight_reduction_pct is not None:
                session_set.weight_reduction_pct = input.weight_reduction_pct
            if input.rest_seconds is not None:
                session_set.rest_seconds = input.rest_seconds

            updated_set = await self.uow.session_repository.update_set(session_set)
            await self.uow.commit()
            return self._map_set_to_dto(updated_set)

    async def remove_set(self, id: UUID) -> bool:
        async with self.uow:
            s = await self.uow.session_repository.get_set_by_id(id)
            if not s:
                raise EntityNotFoundException("SessionSet", id)

            await self.uow.session_repository.delete_set(id)
            await self.uow.commit()
            return True

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
                                muscle_group=MuscleGroupDTO(
                                    id=mg.muscle_group.id, name=mg.muscle_group.name
                                ),
                                role=mg.role,
                            )
                            for mg in se.exercise.muscle_groups
                        ],
                    ),
                    order=se.order,
                    superset_group=se.superset_group,
                    rest_seconds=se.rest_seconds,
                    notes=se.notes,
                    sets=[self._map_set_to_dto(ss) for ss in se.sets],
                )
                for se in session.exercises
            ],
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
            performed_at=ss.performed_at,
        )
