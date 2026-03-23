from dataclasses import dataclass
from strawberry.fastapi import BaseContext
from app.application.services.exercise_service import ExerciseService
from app.application.services.muscle_group_service import MuscleGroupService
from app.application.services.routine_service import RoutineService
from app.application.services.mesocycle_service import MesocycleService
from app.application.services.session_service import SessionService
from app.application.services.bodyweight_service import BodyweightService
from app.application.services.insight_service import InsightService
from app.application.services.calendar_service import CalendarService
from app.application.services.backup_service import BackupService

@dataclass
class Context(BaseContext):
    exercise_service: ExerciseService
    muscle_group_service: MuscleGroupService
    routine_service: RoutineService
    mesocycle_service: MesocycleService
    session_service: SessionService
    bodyweight_service: BodyweightService
    insight_service: InsightService
    calendar_service: CalendarService
    backup_service: BackupService
