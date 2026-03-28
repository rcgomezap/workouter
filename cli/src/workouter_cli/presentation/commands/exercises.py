"""Exercises command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from typing import Any, TypeVar

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
    return asdict(exercise)


@click.group(name="exercises")
def exercises() -> None:
    """Exercise CRUD commands."""


@exercises.command(name="list")
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.pass_obj
def list_exercises(ctx: CLIContext, page: int, page_size: int) -> None:
    """List exercises."""

    items: list[Exercise]
    pagination: dict[str, int]
    items, pagination = _run(ctx.exercise_service.list(page=page, page_size=page_size))
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
