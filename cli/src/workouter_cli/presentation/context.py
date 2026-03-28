"""Click dependency-injection context object."""

from __future__ import annotations

from dataclasses import dataclass

from workouter_cli.application.services.backup_service import BackupService
from workouter_cli.application.services.bodyweight_service import BodyweightService
from workouter_cli.application.services.calendar_service import CalendarService
from workouter_cli.application.services.exercise_service import ExerciseService
from workouter_cli.application.services.insight_service import InsightService
from workouter_cli.application.services.mesocycle_service import MesocycleService
from workouter_cli.application.services.routine_service import RoutineService
from workouter_cli.application.services.session_service import SessionService
from workouter_cli.application.services.workflow_service import WorkflowService
from workouter_cli.infrastructure.config.schema import Config
from workouter_cli.infrastructure.graphql.client import GraphQLClient


@dataclass(slots=True)
class CLIContext:
    """Runtime dependencies shared across commands."""

    config: Config
    client: GraphQLClient
    output_json: bool
    timeout: int
    backup_service: BackupService
    bodyweight_service: BodyweightService
    insight_service: InsightService
    exercise_service: ExerciseService
    mesocycle_service: MesocycleService
    routine_service: RoutineService
    session_service: SessionService
    calendar_service: CalendarService
    workflow_service: WorkflowService
