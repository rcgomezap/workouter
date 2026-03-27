from datetime import date

from pydantic import BaseModel

from app.application.dto.exercise import ExerciseDTO, ExerciseMuscleGroupDTO, MuscleGroupDTO
from app.application.dto.mesocycle import PlannedSessionDTO
from app.application.dto.routine import RoutineDTO, RoutineExerciseDTO, RoutineSetDTO
from app.application.dto.session import SessionDTO, SessionExerciseDTO, SessionSetDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.mesocycle import PlannedSession
from app.domain.entities.routine import Routine, RoutineExercise
from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus


class CalendarDay(BaseModel):
    date: date
    planned_session: PlannedSessionDTO | None = None
    session: SessionDTO | None = None
    is_completed: bool = False
    is_rest_day: bool = True


class CalendarService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_day(self, date_val: date) -> CalendarDay:
        days = await self.get_range(date_val, date_val)
        if days:
            return days[0]
        return CalendarDay(date=date_val, is_rest_day=True)

    async def get_range(self, start_date: date, end_date: date) -> list[CalendarDay]:
        async with self.uow:
            planned_sessions = (
                await self.uow.mesocycle_repository.get_planned_sessions_by_date_range(
                    start_date, end_date
                )
            )
            sessions = await self.uow.session_repository.get_by_date_range(start_date, end_date)

            ps_by_date = {ps.date: ps for ps in planned_sessions}
            s_by_date = {s.started_at.date(): s for s in sessions if s.started_at}

            # If there are multiple sessions on the same day, this logic might need refinement
            # For now, we take the last one or merge. But let's keep it simple.

            calendar_days = []
            import datetime

            delta = end_date - start_date
            for i in range(delta.days + 1):
                current_date = start_date + datetime.timedelta(days=i)
                ps = ps_by_date.get(current_date)
                s = s_by_date.get(current_date)

                is_completed = s.status == SessionStatus.COMPLETED if s else False
                is_rest_day = ps is None

                calendar_days.append(
                    CalendarDay(
                        date=current_date,
                        planned_session=self._map_planned_session_to_dto(ps) if ps else None,
                        session=self._map_session_to_dto(s) if s else None,
                        is_completed=is_completed,
                        is_rest_day=is_rest_day,
                    )
                )

            return calendar_days

    def _map_planned_session_to_dto(self, ps: PlannedSession) -> PlannedSessionDTO:
        return PlannedSessionDTO(
            id=ps.id,
            routine=self._map_routine_to_dto(ps.routine) if ps.routine else None,
            day_of_week=ps.day_of_week,
            date=ps.date,
            notes=ps.notes,
        )

    def _map_session_to_dto(self, session: Session) -> SessionDTO:
        def _map_session_exercise(se: SessionExercise) -> SessionExerciseDTO:
            mgs = se.exercise.muscle_groups if se.exercise.muscle_groups is not None else []
            return SessionExerciseDTO(
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
                        for mg in mgs
                    ],
                ),
                order=se.order,
                superset_group=se.superset_group,
                rest_seconds=se.rest_seconds,
                notes=se.notes,
                sets=[self._map_session_set_to_dto(ss) for ss in se.sets],
            )

        return SessionDTO(
            id=session.id,
            planned_session_id=session.planned_session_id,
            mesocycle_id=session.mesocycle_id,
            routine_id=session.routine_id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            notes=session.notes,
            exercises=[_map_session_exercise(se) for se in session.exercises],
        )

    def _map_session_set_to_dto(self, ss: SessionSet) -> SessionSetDTO:
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

    def _map_routine_to_dto(self, routine: Routine) -> RoutineDTO:
        def _map_routine_exercise(re: RoutineExercise) -> RoutineExerciseDTO:
            mgs = re.exercise.muscle_groups if re.exercise.muscle_groups is not None else []
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
                        for mg in mgs
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

        return RoutineDTO(
            id=routine.id,
            name=routine.name,
            description=routine.description,
            exercises=[_map_routine_exercise(re) for re in routine.exercises],
        )
