"""CLI entry point."""

from __future__ import annotations

import json
from typing import Any

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.application.services.backup_service import BackupService
from workouter_cli.application.services.bodyweight_service import BodyweightService
from workouter_cli.application.services.calendar_service import CalendarService
from workouter_cli.application.services.exercise_service import ExerciseService
from workouter_cli.application.services.insight_service import InsightService
from workouter_cli.application.services.mesocycle_service import MesocycleService
from workouter_cli.application.services.muscle_group_service import MuscleGroupService
from workouter_cli.application.services.routine_service import RoutineService
from workouter_cli.application.services.session_service import SessionService
from workouter_cli.application.services.workflow_service import WorkflowService
from workouter_cli.domain.exceptions import AuthError, CLIError
from workouter_cli.infrastructure.config.loader import ConfigError, load_config
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.repositories.backup import GraphQLBackupRepository
from workouter_cli.infrastructure.repositories.bodyweight import GraphQLBodyweightRepository
from workouter_cli.infrastructure.repositories.calendar import GraphQLCalendarRepository
from workouter_cli.infrastructure.repositories.exercise import GraphQLExerciseRepository
from workouter_cli.infrastructure.repositories.insight import GraphQLInsightRepository
from workouter_cli.infrastructure.repositories.mesocycle import GraphQLMesocycleRepository
from workouter_cli.infrastructure.repositories.muscle_group import GraphQLMuscleGroupRepository
from workouter_cli.infrastructure.repositories.routine import GraphQLRoutineRepository
from workouter_cli.infrastructure.repositories.session import GraphQLSessionRepository
from workouter_cli.presentation.commands.backup import backup
from workouter_cli.presentation.commands.bodyweight import bodyweight
from workouter_cli.presentation.commands.calendar import calendar
from workouter_cli.presentation.commands.exercises import exercises
from workouter_cli.presentation.commands.insights import insights
from workouter_cli.presentation.commands.mesocycles import mesocycles
from workouter_cli.presentation.commands.muscle_groups import muscle_groups
from workouter_cli.presentation.commands.routines import routines
from workouter_cli.presentation.commands.sessions import sessions
from workouter_cli.presentation.commands.workout import workout
from workouter_cli.presentation.context import CLIContext
from workouter_cli.presentation.middleware.error_handler import (
    handle_cli_error,
    handle_unexpected_error,
)
from workouter_cli.presentation.middleware.logging import setup_logging
from workouter_cli.utils.exit_codes import ExitCode
from workouter_cli.version import __version__


class SafeGroup(click.Group):
    """Click group with centralized CLI error handling."""

    def invoke(self, ctx: click.Context) -> object:
        output_json = bool(ctx.params.get("output_json", False))
        command = ctx.command_path

        try:
            return super().invoke(ctx)
        except CLIError as error:
            handle_cli_error(error, output_json=output_json, command=command)
        except click.exceptions.Exit:
            raise
        except click.ClickException:
            raise
        except Exception as error:  # pragma: no cover - defensive fallback
            handle_unexpected_error(error, output_json=output_json, command=command)


EXAMPLE_OUTPUTS: dict[str, dict[str, Any]] = {
    "exercises list": {
        "success": True,
        "data": {
            "items": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Bench Press",
                    "description": "Compound chest exercise",
                    "equipment": "Barbell",
                    "muscle_groups": [
                        {
                            "muscle_group": {
                                "id": "11111111-1111-1111-1111-111111111111",
                                "name": "Chest",
                            },
                            "role": "PRIMARY",
                        }
                    ],
                }
            ],
            "total": 42,
            "page": 1,
            "page_size": 20,
            "total_pages": 3,
        },
    }
}


def _normalize_type_name(parameter_type: click.types.ParamType) -> str:
    if isinstance(parameter_type, click.types.BoolParamType):
        return "boolean"
    if isinstance(parameter_type, click.types.IntParamType):
        return "int"
    if isinstance(parameter_type, click.types.UUIDParameterType):
        return "UUID"
    return parameter_type.name or parameter_type.__class__.__name__.lower()


def _resolve_command(command_name: str) -> tuple[click.Command, str]:
    parts = [part for part in command_name.split() if part]
    if not parts:
        raise click.ClickException("Command name is required")

    current: click.Command | click.Group = cli
    resolved_parts: list[str] = []

    for part in parts:
        if not isinstance(current, click.Group):
            path = " ".join(resolved_parts)
            raise click.ClickException(f"'{path}' has no subcommands")
        next_command = current.commands.get(part)
        if next_command is None:
            raise click.ClickException(f"Unknown command: {' '.join(parts)}")
        current = next_command
        resolved_parts.append(part)

    return current, " ".join(resolved_parts)


def _build_schema(command_name: str) -> dict[str, Any]:
    command, normalized_name = _resolve_command(command_name)
    options: list[dict[str, Any]] = []
    arguments: list[dict[str, Any]] = []
    required_flags: list[str] = []

    for parameter in command.params:
        if isinstance(parameter, click.Option):
            long_flags = [flag for flag in parameter.opts if flag.startswith("--")]
            flag_name = long_flags[0] if long_flags else parameter.opts[0]
            option_schema: dict[str, Any] = {
                "name": flag_name,
                "type": _normalize_type_name(parameter.type),
                "required": parameter.required,
                "description": parameter.help or "",
            }
            default_value = parameter.default
            if isinstance(default_value, (str, int, float, bool, list, dict, tuple)):
                option_schema["default"] = default_value
            options.append(option_schema)
            if parameter.required and flag_name.startswith("--"):
                required_flags.append(flag_name)
            continue

        if isinstance(parameter, click.Argument):
            arguments.append(
                {
                    "name": parameter.name,
                    "type": _normalize_type_name(parameter.type),
                    "required": parameter.required,
                }
            )

    return {
        "command": normalized_name,
        "description": command.help or command.short_help or "",
        "options": options,
        "arguments": arguments,
        "required_flags": required_flags,
        "example_output": EXAMPLE_OUTPUTS.get(
            normalized_name,
            {
                "success": True,
                "data": {},
            },
        ),
    }


@click.group(cls=SafeGroup)
@click.option("--json", "output_json", is_flag=True, help="Output machine-readable JSON")
@click.option("--timeout", type=int, default=None, help="Override request timeout in seconds")
@click.version_option(version=__version__, package_name="workouter-cli")
@click.pass_context
def cli(ctx: click.Context, output_json: bool, timeout: int | None) -> None:
    """Workouter CLI."""

    if ctx.resilient_parsing:
        return

    if ctx.invoked_subcommand is None:
        return

    if ctx.invoked_subcommand == "schema":
        return

    try:
        config = load_config()
        effective_timeout = timeout if timeout is not None else config.timeout
        setup_logging(config)
        client = GraphQLClient(
            url=str(config.api_url), api_key=config.api_key, timeout=effective_timeout
        )
        exercise_repository = GraphQLExerciseRepository(client=client)
        mesocycle_repository = GraphQLMesocycleRepository(client=client)
        routine_repository = GraphQLRoutineRepository(client=client)
        session_repository = GraphQLSessionRepository(client=client)
        calendar_repository = GraphQLCalendarRepository(client=client)
        bodyweight_repository = GraphQLBodyweightRepository(client=client)
        insight_repository = GraphQLInsightRepository(client=client)
        backup_repository = GraphQLBackupRepository(client=client)
        muscle_group_repository = GraphQLMuscleGroupRepository(client=client)
        exercise_service = ExerciseService(exercise_repository=exercise_repository)
        mesocycle_service = MesocycleService(mesocycle_repository=mesocycle_repository)
        routine_service = RoutineService(routine_repository=routine_repository)
        session_service = SessionService(session_repository=session_repository)
        calendar_service = CalendarService(calendar_repository=calendar_repository)
        bodyweight_service = BodyweightService(bodyweight_repository=bodyweight_repository)
        insight_service = InsightService(insight_repository=insight_repository)
        backup_service = BackupService(backup_repository=backup_repository)
        muscle_group_service = MuscleGroupService(muscle_group_repository=muscle_group_repository)
        workflow_service = WorkflowService(
            calendar_repository=calendar_repository,
            session_repository=session_repository,
        )
        ctx.obj = CLIContext(
            config=config,
            client=client,
            output_json=output_json,
            timeout=effective_timeout,
            backup_service=backup_service,
            bodyweight_service=bodyweight_service,
            insight_service=insight_service,
            exercise_service=exercise_service,
            mesocycle_service=mesocycle_service,
            muscle_group_service=muscle_group_service,
            routine_service=routine_service,
            session_service=session_service,
            calendar_service=calendar_service,
            workflow_service=workflow_service,
        )
    except ConfigError as error:
        code = "AUTH_ERROR" if error.exit_code == ExitCode.AUTH_ERROR else "VALIDATION_ERROR"
        handle_cli_error(
            CLIError(message=str(error), exit_code=error.exit_code, code=code),
            output_json=output_json,
            command=ctx.command_path,
        )


@cli.command(name="schema")
@click.argument("command_name", type=str)
def schema(command_name: str) -> None:
    """Show JSON schema for a command."""

    payload = _build_schema(command_name)
    click.echo(json.dumps(payload, separators=(",", ":"), sort_keys=False))


@cli.command(name="ping")
@click.pass_obj
def ping(ctx: CLIContext) -> None:
    """Validate startup and print ready."""

    formatter = get_formatter(ctx.output_json)
    payload = {"message": "ready", "timeout": ctx.timeout}
    rendered = formatter.format(payload, command="ping")

    if isinstance(rendered, str):
        click.echo(rendered)
    else:
        Console().print(rendered)


@cli.command(name="raise-auth", hidden=True)
def raise_auth() -> None:
    """Test-only command that raises AuthError."""

    raise AuthError("Invalid API key")


cli.add_command(exercises)
cli.add_command(mesocycles)
cli.add_command(routines)
cli.add_command(sessions)
cli.add_command(bodyweight)
cli.add_command(insights)
cli.add_command(calendar)
cli.add_command(backup)
cli.add_command(workout)
cli.add_command(muscle_groups)


if __name__ == "__main__":
    cli()
