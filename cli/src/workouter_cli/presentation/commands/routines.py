"""Routines command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Mapping
from dataclasses import asdict
from typing import Any, TypeVar
from uuid import UUID

import click
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console

from workouter_cli.application.dto.routine import CreateRoutineInputDTO, UpdateRoutineInputDTO
from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet
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


def _require_any_update(payload: Mapping[str, object], message: str) -> None:
    if not payload:
        raise ValidationError(message)


def _routine_to_payload(routine: Routine) -> dict[str, object]:
    return asdict(routine)


@click.group(name="routines")
def routines() -> None:
    """Routine composition commands."""


@routines.command(name="list")
@click.option("--page", type=click.IntRange(min=1), default=1, show_default=True)
@click.option("--page-size", type=click.IntRange(min=1, max=100), default=20, show_default=True)
@click.pass_obj
def list_routines(ctx: CLIContext, page: int, page_size: int) -> None:
    """List routines."""

    items: list[Routine]
    pagination: dict[str, int]
    items, pagination = _run(ctx.routine_service.list(page=page, page_size=page_size))
    payload = {
        "items": [_routine_to_payload(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="routines list")


@routines.command(name="get")
@click.argument("routine_id", type=click.UUID)
@click.pass_obj
def get_routine(ctx: CLIContext, routine_id: UUID) -> None:
    """Get one routine by ID."""

    routine: Routine = _run(ctx.routine_service.get(str(routine_id)))
    _render(ctx, _routine_to_payload(routine), command="routines get")


@routines.command(name="create")
@click.option("--name", required=True, type=str)
@click.option("--description", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without creating")
@click.pass_obj
def create_routine(
    ctx: CLIContext,
    name: str,
    description: str | None,
    dry_run: bool,
) -> None:
    """Create routine."""

    try:
        dto = CreateRoutineInputDTO(name=name, description=description)
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid create payload: {message}") from error

    payload = dto.model_dump(exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {"dry_run": True, "operation": "createRoutine", "input": payload},
            command="routines create",
        )
        return

    routine: Routine = _run(ctx.routine_service.create(dto))
    _render(ctx, _routine_to_payload(routine), command="routines create")


@routines.command(name="update")
@click.argument("routine_id", type=click.UUID)
@click.option("--name", type=str, default=None)
@click.option("--description", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without updating")
@click.pass_obj
def update_routine(
    ctx: CLIContext,
    routine_id: UUID,
    name: str | None,
    description: str | None,
    dry_run: bool,
) -> None:
    """Update routine."""

    if name is None and description is None:
        raise ValidationError("Provide at least one field to update")

    try:
        dto = UpdateRoutineInputDTO(name=name, description=description)
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid update payload: {message}") from error

    payload = dto.model_dump(exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateRoutine",
                "id": str(routine_id),
                "input": payload,
            },
            command="routines update",
        )
        return

    routine: Routine = _run(ctx.routine_service.update(str(routine_id), dto))
    _render(ctx, _routine_to_payload(routine), command="routines update")


@routines.command(name="delete")
@click.argument("routine_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def delete_routine(ctx: CLIContext, routine_id: UUID, force: bool) -> None:
    """Delete routine."""

    if not force:
        raise ValidationError("Use --force to delete routine")

    deleted: bool = _run(ctx.routine_service.delete(str(routine_id)))
    _render(ctx, {"id": str(routine_id), "deleted": deleted}, command="routines delete")


@routines.command(name="add-exercise")
@click.argument("routine_id", type=click.UUID)
@click.option("--exercise-id", type=click.UUID, required=True)
@click.option("--order", type=click.IntRange(min=1), required=True)
@click.option("--superset-group", type=click.IntRange(min=1), default=None)
@click.option("--rest-seconds", type=click.IntRange(min=0), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_routine_exercise(
    ctx: CLIContext,
    routine_id: UUID,
    exercise_id: UUID,
    order: int,
    superset_group: int | None,
    rest_seconds: int | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Add exercise to a routine."""

    payload: dict[str, object] = {
        "exerciseId": str(exercise_id),
        "order": order,
    }
    if superset_group is not None:
        payload["supersetGroup"] = superset_group
    if rest_seconds is not None:
        payload["restSeconds"] = rest_seconds
    if notes is not None:
        payload["notes"] = notes

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "addRoutineExercise",
                "routine_id": str(routine_id),
                "input": payload,
            },
            command="routines add-exercise",
        )
        return

    routine: Routine = _run(ctx.routine_service.add_exercise(str(routine_id), payload))
    _render(ctx, asdict(routine), command="routines add-exercise")


@routines.command(name="update-exercise")
@click.argument("routine_exercise_id", type=click.UUID)
@click.option("--order", type=click.IntRange(min=1), default=None)
@click.option("--superset-group", type=click.IntRange(min=1), default=None)
@click.option("--rest-seconds", type=click.IntRange(min=0), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_routine_exercise(
    ctx: CLIContext,
    routine_exercise_id: UUID,
    order: int | None,
    superset_group: int | None,
    rest_seconds: int | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Update one routine exercise."""

    payload: dict[str, object] = {}
    if order is not None:
        payload["order"] = order
    if superset_group is not None:
        payload["supersetGroup"] = superset_group
    if rest_seconds is not None:
        payload["restSeconds"] = rest_seconds
    if notes is not None:
        payload["notes"] = notes

    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateRoutineExercise",
                "id": str(routine_exercise_id),
                "input": payload,
            },
            command="routines update-exercise",
        )
        return

    routine_exercise: RoutineExercise = _run(
        ctx.routine_service.update_exercise(str(routine_exercise_id), payload)
    )
    _render(ctx, asdict(routine_exercise), command="routines update-exercise")


@routines.command(name="remove-exercise")
@click.argument("routine_exercise_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_routine_exercise(ctx: CLIContext, routine_exercise_id: UUID, force: bool) -> None:
    """Remove one exercise from a routine."""

    if not force:
        raise ValidationError("Use --force to remove routine exercise")

    deleted: bool = _run(ctx.routine_service.remove_exercise(str(routine_exercise_id)))
    _render(
        ctx,
        {"id": str(routine_exercise_id), "deleted": deleted},
        command="routines remove-exercise",
    )


@routines.command(name="add-set")
@click.argument("routine_exercise_id", type=click.UUID)
@click.option("--set-number", type=click.IntRange(min=1), required=True)
@click.option(
    "--set-type",
    type=click.Choice(["STANDARD", "DROPSET"], case_sensitive=True),
    required=True,
)
@click.option("--target-reps-min", type=click.IntRange(min=1), default=None)
@click.option("--target-reps-max", type=click.IntRange(min=1), default=None)
@click.option("--target-rir", type=click.IntRange(min=0), default=None)
@click.option("--target-weight", type=click.FloatRange(min=0), default=None)
@click.option("--weight-reduction-pct", type=click.FloatRange(min=0, max=100), default=None)
@click.option("--rest-seconds", type=click.IntRange(min=0), default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_routine_set(
    ctx: CLIContext,
    routine_exercise_id: UUID,
    set_number: int,
    set_type: str,
    target_reps_min: int | None,
    target_reps_max: int | None,
    target_rir: int | None,
    target_weight: float | None,
    weight_reduction_pct: float | None,
    rest_seconds: int | None,
    dry_run: bool,
) -> None:
    """Add set to a routine exercise."""

    if (
        target_reps_min is not None
        and target_reps_max is not None
        and target_reps_min > target_reps_max
    ):
        raise ValidationError("--target-reps-min cannot be greater than --target-reps-max")

    payload: dict[str, object] = {
        "setNumber": set_number,
        "setType": set_type,
    }
    if target_reps_min is not None:
        payload["targetRepsMin"] = target_reps_min
    if target_reps_max is not None:
        payload["targetRepsMax"] = target_reps_max
    if target_rir is not None:
        payload["targetRir"] = target_rir
    if target_weight is not None:
        payload["targetWeightKg"] = target_weight
    if weight_reduction_pct is not None:
        payload["weightReductionPct"] = weight_reduction_pct
    if rest_seconds is not None:
        payload["restSeconds"] = rest_seconds

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "addRoutineSet",
                "routine_exercise_id": str(routine_exercise_id),
                "input": payload,
            },
            command="routines add-set",
        )
        return

    routine_exercise: RoutineExercise = _run(
        ctx.routine_service.add_set(str(routine_exercise_id), payload)
    )
    _render(ctx, asdict(routine_exercise), command="routines add-set")


@routines.command(name="update-set")
@click.argument("set_id", type=click.UUID)
@click.option("--set-number", type=click.IntRange(min=1), default=None)
@click.option(
    "--set-type",
    type=click.Choice(["STANDARD", "DROPSET"], case_sensitive=True),
    default=None,
)
@click.option("--target-reps-min", type=click.IntRange(min=1), default=None)
@click.option("--target-reps-max", type=click.IntRange(min=1), default=None)
@click.option("--target-rir", type=click.IntRange(min=0), default=None)
@click.option("--target-weight", type=click.FloatRange(min=0), default=None)
@click.option("--weight-reduction-pct", type=click.FloatRange(min=0, max=100), default=None)
@click.option("--rest-seconds", type=click.IntRange(min=0), default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_routine_set(
    ctx: CLIContext,
    set_id: UUID,
    set_number: int | None,
    set_type: str | None,
    target_reps_min: int | None,
    target_reps_max: int | None,
    target_rir: int | None,
    target_weight: float | None,
    weight_reduction_pct: float | None,
    rest_seconds: int | None,
    dry_run: bool,
) -> None:
    """Update one routine set."""

    if (
        target_reps_min is not None
        and target_reps_max is not None
        and target_reps_min > target_reps_max
    ):
        raise ValidationError("--target-reps-min cannot be greater than --target-reps-max")

    payload: dict[str, object] = {}
    if set_number is not None:
        payload["setNumber"] = set_number
    if set_type is not None:
        payload["setType"] = set_type
    if target_reps_min is not None:
        payload["targetRepsMin"] = target_reps_min
    if target_reps_max is not None:
        payload["targetRepsMax"] = target_reps_max
    if target_rir is not None:
        payload["targetRir"] = target_rir
    if target_weight is not None:
        payload["targetWeightKg"] = target_weight
    if weight_reduction_pct is not None:
        payload["weightReductionPct"] = weight_reduction_pct
    if rest_seconds is not None:
        payload["restSeconds"] = rest_seconds

    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateRoutineSet",
                "id": str(set_id),
                "input": payload,
            },
            command="routines update-set",
        )
        return

    routine_set: RoutineSet = _run(ctx.routine_service.update_set(str(set_id), payload))
    _render(ctx, asdict(routine_set), command="routines update-set")


@routines.command(name="remove-set")
@click.argument("set_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_routine_set(ctx: CLIContext, set_id: UUID, force: bool) -> None:
    """Remove one set from a routine exercise."""

    if not force:
        raise ValidationError("Use --force to remove routine set")

    deleted: bool = _run(ctx.routine_service.remove_set(str(set_id)))
    _render(ctx, {"id": str(set_id), "deleted": deleted}, command="routines remove-set")
