"""Exercises command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from typing import Any, TypeVar
from uuid import UUID

import click
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console

from workouter_cli.application.dto.exercise import CreateExerciseInputDTO, UpdateExerciseInputDTO
from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.exercise import Exercise
from workouter_cli.domain.exceptions import ValidationError
from workouter_cli.presentation.context import CLIContext


T = TypeVar("T")


def _run(coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


def _render(ctx: CLIContext, payload: object, command: str) -> None:
    formatter = get_formatter(ctx.output_json)
    rendered = formatter.format(payload, command=command)
    if isinstance(rendered, str):
        click.echo(rendered)
    else:
        Console().print(rendered)


def _exercise_to_payload(exercise: Exercise) -> dict[str, object]:
    """Convert exercise to display payload with formatted muscle groups."""
    data = asdict(exercise)

    # Format muscle groups for display
    if exercise.muscle_groups:
        primary_muscles = [
            emg.muscle_group.name for emg in exercise.muscle_groups if emg.role == "PRIMARY"
        ]
        secondary_muscles = [
            emg.muscle_group.name for emg in exercise.muscle_groups if emg.role == "SECONDARY"
        ]

        # Add formatted strings for table display
        data["primary_muscles"] = ", ".join(primary_muscles) if primary_muscles else "-"
        data["secondary_muscles"] = ", ".join(secondary_muscles) if secondary_muscles else "-"
    else:
        data["primary_muscles"] = "-"
        data["secondary_muscles"] = "-"

    return data


@click.group(name="exercises")
def exercises() -> None:
    """Exercise CRUD commands."""


@exercises.command(name="list")
@click.option("--muscle-group-id", type=click.UUID, default=None)
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.pass_obj
def list_exercises(
    ctx: CLIContext, muscle_group_id: UUID | None, page: int, page_size: int
) -> None:
    """List exercises."""

    items: list[Exercise]
    pagination: dict[str, int]
    items, pagination = _run(
        ctx.exercise_service.list(
            page=page,
            page_size=page_size,
            muscle_group_id=str(muscle_group_id) if muscle_group_id is not None else None,
        )
    )
    payload = {
        "items": [_exercise_to_payload(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="exercises list")


@exercises.command(name="get")
@click.argument("exercise_id")
@click.pass_obj
def get_exercise(ctx: CLIContext, exercise_id: str) -> None:
    """Get one exercise by ID."""

    exercise: Exercise
    exercise = _run(ctx.exercise_service.get(exercise_id))
    _render(ctx, _exercise_to_payload(exercise), command="exercises get")


@exercises.command(name="create")
@click.option("--name", required=True, type=str)
@click.option("--description", type=str, default=None)
@click.option("--equipment", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without creating")
@click.pass_obj
def create_exercise(
    ctx: CLIContext,
    name: str,
    description: str | None,
    equipment: str | None,
    dry_run: bool,
) -> None:
    """Create exercise."""

    try:
        dto = CreateExerciseInputDTO(name=name, description=description, equipment=equipment)
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid create payload: {message}") from error

    payload = dto.model_dump(exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {"dry_run": True, "operation": "createExercise", "input": payload},
            command="exercises create",
        )
        return

    exercise: Exercise = _run(ctx.exercise_service.create(dto))
    _render(ctx, _exercise_to_payload(exercise), command="exercises create")


@exercises.command(name="update")
@click.argument("exercise_id")
@click.option("--name", type=str, default=None)
@click.option("--description", type=str, default=None)
@click.option("--equipment", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without updating")
@click.pass_obj
def update_exercise(
    ctx: CLIContext,
    exercise_id: str,
    name: str | None,
    description: str | None,
    equipment: str | None,
    dry_run: bool,
) -> None:
    """Update exercise."""

    if name is None and description is None and equipment is None:
        raise ValidationError("Provide at least one field to update")

    try:
        dto = UpdateExerciseInputDTO(name=name, description=description, equipment=equipment)
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid update payload: {message}") from error

    payload = dto.model_dump(exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateExercise",
                "id": exercise_id,
                "input": payload,
            },
            command="exercises update",
        )
        return

    exercise: Exercise = _run(ctx.exercise_service.update(exercise_id, dto))
    _render(ctx, _exercise_to_payload(exercise), command="exercises update")


@exercises.command(name="delete")
@click.argument("exercise_id")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def delete_exercise(ctx: CLIContext, exercise_id: str, force: bool) -> None:
    """Delete exercise."""

    if not force:
        raise ValidationError("Use --force to delete exercise")

    deleted: bool = _run(ctx.exercise_service.delete(exercise_id))
    _render(ctx, {"id": exercise_id, "deleted": deleted}, command="exercises delete")


@exercises.command(name="assign-muscles")
@click.argument("exercise_id")
@click.option(
    "--primary",
    "primary_ids",
    multiple=True,
    help="Primary muscle group (name or UUID). Can specify multiple times.",
)
@click.option(
    "--secondary",
    "secondary_ids",
    multiple=True,
    help="Secondary muscle group (name or UUID). Can specify multiple times.",
)
@click.option("--dry-run", is_flag=True, help="Show what would be changed without applying")
@click.pass_obj
def assign_muscles(
    ctx: CLIContext,
    exercise_id: str,
    primary_ids: tuple[str, ...],
    secondary_ids: tuple[str, ...],
    dry_run: bool,
) -> None:
    """
    Assign muscle groups to an exercise.

    Replaces all existing muscle group assignments.

    Examples:

      # Assign by name (case-insensitive)
      workouter-cli exercises assign-muscles <id> --primary chest --secondary triceps

      # Assign by UUID
      workouter-cli exercises assign-muscles <id> --primary <uuid>

      # Multiple primary muscles
      workouter-cli exercises assign-muscles <id> --primary chest --primary shoulders

      # Clear all assignments (no muscle groups)
      workouter-cli exercises assign-muscles <id>
    """
    all_muscle_groups = _run(ctx.muscle_group_service.list_all())

    try:
        resolved_primary = ctx.muscle_group_service.resolve_muscle_group_ids_from_catalog(
            primary_ids,
            all_muscle_groups,
        )
        resolved_secondary = ctx.muscle_group_service.resolve_muscle_group_ids_from_catalog(
            secondary_ids,
            all_muscle_groups,
        )
    except ValueError as e:
        raise ValidationError(str(e)) from e

    if dry_run:
        # Fetch current exercise to show diff
        current_exercise: Exercise = _run(ctx.exercise_service.get(exercise_id))
        current_primary = [
            emg.muscle_group.name for emg in current_exercise.muscle_groups if emg.role == "PRIMARY"
        ]
        current_secondary = [
            emg.muscle_group.name
            for emg in current_exercise.muscle_groups
            if emg.role == "SECONDARY"
        ]

        id_to_name = {mg.id: mg.name for mg in all_muscle_groups}

        new_primary = [id_to_name[mg_id] for mg_id in resolved_primary]
        new_secondary = [id_to_name[mg_id] for mg_id in resolved_secondary]

        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "assignMuscleGroups",
                "exercise_id": exercise_id,
                "exercise_name": current_exercise.name,
                "current_primary": current_primary if current_primary else ["-"],
                "current_secondary": current_secondary if current_secondary else ["-"],
                "new_primary": new_primary if new_primary else ["-"],
                "new_secondary": new_secondary if new_secondary else ["-"],
            },
            command="exercises assign-muscles",
        )
        return

    # Apply the assignment
    exercise: Exercise = _run(
        ctx.exercise_service.assign_muscle_groups(
            exercise_id,
            resolved_primary,
            resolved_secondary,
        )
    )
    _render(ctx, _exercise_to_payload(exercise), command="exercises assign-muscles")
