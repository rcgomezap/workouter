from uuid import UUID
from collections import defaultdict
from app.application.dto.insight import (
    MuscleGroupVolume,
    ProgressiveOverloadInsight,
    VolumeInsight,
    WeeklyExerciseProgress,
    WeeklyVolume,
    IntensityInsight,
    WeeklyIntensity,
)
from app.application.dto.pagination import PaginatedResult, PaginationInput
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.enums import SessionStatus


class InsightService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_volume_insight(
        self, mesocycle_id: UUID, muscle_group_id: UUID | None = None
    ) -> VolumeInsight:
        async with self.uow:
            mesocycle = await self.uow.mesocycle_repository.get_by_id(mesocycle_id)
            if not mesocycle:
                return VolumeInsight(
                    mesocycle_id=mesocycle_id,
                    weekly_volumes=[],
                    total_sets=0,
                    muscle_group_breakdown=[],
                )

            sessions = await self.uow.session_repository.list_by_filters(
                mesocycle_id=mesocycle_id, status=SessionStatus.COMPLETED, limit=1000
            )

            # Map week_id to week_number
            week_map = {w.id: w.week_number for w in mesocycle.weeks}

            weekly_sets = defaultdict(int)
            muscle_group_sets = defaultdict(int)
            total_sets = 0

            for session in sessions:
                if not session.planned_session_id:
                    continue

                # We need the week_id from planned_session
                planned_session = await self.uow.mesocycle_repository.get_planned_session_by_id(
                    session.planned_session_id
                )
                if not planned_session:
                    continue

                week_num = None
                if planned_session.mesocycle_week_id is not None:
                    week_num = week_map.get(planned_session.mesocycle_week_id)

                if week_num is None:
                    continue

                for ex in session.exercises:
                    # Filter by muscle group if requested
                    is_target = False
                    mg_ids = [mg.muscle_group.id for mg in ex.exercise.muscle_groups]

                    if muscle_group_id is None or muscle_group_id in mg_ids:
                        is_target = True

                    if is_target:
                        working_sets = len([s for s in ex.sets if s.actual_reps is not None])
                        weekly_sets[week_num] += working_sets
                        total_sets += working_sets

                        for mg_info in ex.exercise.muscle_groups:
                            muscle_group_sets[
                                (mg_info.muscle_group.id, mg_info.muscle_group.name)
                            ] += working_sets

            weekly_volumes = [
                WeeklyVolume(week_number=wn, sets_count=count)
                for wn, count in sorted(weekly_sets.items())
            ]

            muscle_group_breakdown = [
                MuscleGroupVolume(muscle_group_id=mg[0], muscle_group_name=mg[1], sets_count=count)
                for mg, count in muscle_group_sets.items()
            ]

            return VolumeInsight(
                mesocycle_id=mesocycle_id,
                weekly_volumes=weekly_volumes,
                total_sets=total_sets,
                muscle_group_breakdown=muscle_group_breakdown,
            )

    async def get_exercise_history(self, exercise_id: UUID, pagination: PaginationInput):
        async with self.uow:
            offset = (pagination.page - 1) * pagination.page_size
            items = await self.uow.session_repository.list_by_filters(
                exercise_id=exercise_id,
                offset=offset,
                limit=pagination.page_size,
            )
            total = await self.uow.session_repository.count_by_filters(exercise_id=exercise_id)

            total_pages = (
                (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0
            )

            return PaginatedResult(
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages,
            )

    async def get_progressive_overload_insight(
        self, mesocycle_id: UUID, exercise_id: UUID
    ) -> ProgressiveOverloadInsight:
        async with self.uow:
            mesocycle = await self.uow.mesocycle_repository.get_by_id(mesocycle_id)
            if not mesocycle:
                return ProgressiveOverloadInsight(
                    exercise_id=exercise_id,
                    mesocycle_id=mesocycle_id,
                    weekly_progress=[],
                    estimated_one_rep_max_progression=[],
                )

            sessions = await self.uow.session_repository.list_by_filters(
                mesocycle_id=mesocycle_id,
                exercise_id=exercise_id,
                status=SessionStatus.COMPLETED,
                limit=1000,
            )

            week_map = {w.id: w.week_number for w in mesocycle.weeks}

            # week_num -> list of sets
            weekly_sets_data = defaultdict(list)

            for session in sessions:
                if not session.planned_session_id:
                    continue

                planned_session = await self.uow.mesocycle_repository.get_planned_session_by_id(
                    session.planned_session_id
                )
                if not planned_session:
                    continue

                week_num = None
                if planned_session.mesocycle_week_id is not None:
                    week_num = week_map.get(planned_session.mesocycle_week_id)

                if week_num is None:
                    continue

                for ex in session.exercises:
                    if ex.exercise.id == exercise_id:
                        weekly_sets_data[week_num].extend(ex.sets)

            weekly_progress = []
            e1rm_progression = []

            for week_num in sorted(weekly_sets_data.keys()):
                sets = weekly_sets_data[week_num]
                valid_sets = [
                    s for s in sets if s.actual_weight_kg is not None and s.actual_reps is not None
                ]

                if not valid_sets:
                    continue

                max_weight = float(max(s.actual_weight_kg for s in valid_sets))
                avg_reps = sum(s.actual_reps for s in valid_sets) / len(valid_sets)

                rirs = [s.actual_rir for s in valid_sets if s.actual_rir is not None]
                avg_rir = sum(rirs) / len(rirs) if rirs else 0.0

                e1rms = [
                    float(s.calculate_epley_1rm())
                    for s in valid_sets
                    if s.calculate_epley_1rm() is not None
                ]
                best_e1rm = max(e1rms) if e1rms else 0.0

                weekly_progress.append(
                    WeeklyExerciseProgress(
                        week_number=week_num,
                        max_weight_kg=max_weight,
                        avg_reps=avg_reps,
                        avg_rir=avg_rir,
                    )
                )
                e1rm_progression.append(best_e1rm)

            return ProgressiveOverloadInsight(
                exercise_id=exercise_id,
                mesocycle_id=mesocycle_id,
                weekly_progress=weekly_progress,
                estimated_one_rep_max_progression=e1rm_progression,
            )

    async def get_intensity_insight(self, mesocycle_id: UUID) -> IntensityInsight:
        async with self.uow:
            mesocycle = await self.uow.mesocycle_repository.get_by_id(mesocycle_id)
            if not mesocycle:
                return IntensityInsight(
                    mesocycle_id=mesocycle_id,
                    weekly_intensities=[],
                    overall_avg_rir=0.0,
                )

            sessions = await self.uow.session_repository.list_by_filters(
                mesocycle_id=mesocycle_id, status=SessionStatus.COMPLETED, limit=1000
            )

            week_map = {w.id: w.week_number for w in mesocycle.weeks}
            weekly_rirs = defaultdict(list)
            all_rirs = []

            for session in sessions:
                if not session.planned_session_id:
                    continue

                planned_session = await self.uow.mesocycle_repository.get_planned_session_by_id(
                    session.planned_session_id
                )
                if not planned_session:
                    continue

                week_num = None
                if planned_session.mesocycle_week_id is not None:
                    week_num = week_map.get(planned_session.mesocycle_week_id)
                if week_num is None:
                    continue

                for ex in session.exercises:
                    for s in ex.sets:
                        if s.actual_rir is not None:
                            weekly_rirs[week_num].append(float(s.actual_rir))
                            all_rirs.append(float(s.actual_rir))

            weekly_intensities = [
                WeeklyIntensity(week_number=wn, avg_rir=sum(rirs) / len(rirs))
                for wn, rirs in sorted(weekly_rirs.items())
            ]

            overall_avg_rir = sum(all_rirs) / len(all_rirs) if all_rirs else 0.0

            return IntensityInsight(
                mesocycle_id=mesocycle_id,
                weekly_intensities=weekly_intensities,
                overall_avg_rir=overall_avg_rir,
            )
