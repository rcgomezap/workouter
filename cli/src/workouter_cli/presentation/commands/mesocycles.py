"""Mesocycles command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from datetime import date, datetime
from typing import Any, TypeVar
from uuid import UUID

import click
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console

from workouter_cli.application.dto.mesocycle import (
    AddMesocycleWeekInputDTO,
    AddPlannedSessionInputDTO,
    CreateMesocycleInputDTO,
    UpdateMesocycleWeekInputDTO,
    UpdateMesocycleInputDTO,
    UpdatePlannedSessionInputDTO,
)
from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.mesocycle import (
    Mesocycle,
    MesocyclePlannedSession,
    MesocycleWeek,
)
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


def _mesocycle_to_payload(mesocycle: Mesocycle) -> dict[str, object]:
    return asdict(mesocycle)


def _to_date(value: datetime | None) -> date | None:
    return value.date() if value is not None else None


def _require_any_update(payload: dict[str, object], message: str) -> None:
    if not payload:
        raise ValidationError(message)


@click.group(name="mesocycles")
def mesocycles() -> None:
    """Mesocycle CRUD commands."""


@mesocycles.command(name="list")
@click.option("--page", type=click.IntRange(min=1), default=1, show_default=True)
@click.option("--page-size", type=click.IntRange(min=1, max=100), default=20, show_default=True)
@click.option(
    "--status",
    type=click.Choice(["PLANNED", "ACTIVE", "COMPLETED"], case_sensitive=True),
    default=None,
)
@click.pass_obj
def list_mesocycles(ctx: CLIContext, page: int, page_size: int, status: str | None) -> None:
    """List mesocycles."""

    items: list[Mesocycle]
    pagination: dict[str, int]
    items, pagination = _run(
        ctx.mesocycle_service.list(page=page, page_size=page_size, status=status)
    )
    payload = {
        "items": [_mesocycle_to_payload(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="mesocycles list")


@mesocycles.command(name="get")
@click.argument("mesocycle_id", type=click.UUID)
@click.pass_obj
def get_mesocycle(ctx: CLIContext, mesocycle_id: UUID) -> None:
    """Get one mesocycle by ID."""

    mesocycle: Mesocycle = _run(ctx.mesocycle_service.get(str(mesocycle_id)))
    _render(ctx, _mesocycle_to_payload(mesocycle), command="mesocycles get")


@mesocycles.command(name="create")
@click.option("--name", required=True, type=str)
@click.option("--description", type=str, default=None)
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--dry-run", is_flag=True, help="Validate without creating")
@click.pass_obj
def create_mesocycle(
    ctx: CLIContext,
    name: str,
    description: str | None,
    start_date: datetime,
    dry_run: bool,
) -> None:
    """Create mesocycle."""

    try:
        dto = CreateMesocycleInputDTO(
            name=name,
            description=description,
            startDate=start_date.date(),
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid create payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {"dry_run": True, "operation": "createMesocycle", "input": payload},
            command="mesocycles create",
        )
        return

    mesocycle: Mesocycle = _run(ctx.mesocycle_service.create(dto))
    _render(ctx, _mesocycle_to_payload(mesocycle), command="mesocycles create")


@mesocycles.command(name="update")
@click.argument("mesocycle_id", type=click.UUID)
@click.option("--name", type=str, default=None)
@click.option("--description", type=str, default=None)
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option(
    "--status",
    type=click.Choice(["PLANNED", "ACTIVE", "COMPLETED"], case_sensitive=True),
    default=None,
)
@click.option("--dry-run", is_flag=True, help="Validate without updating")
@click.pass_obj
def update_mesocycle(
    ctx: CLIContext,
    mesocycle_id: UUID,
    name: str | None,
    description: str | None,
    start_date: datetime | None,
    end_date: datetime | None,
    status: str | None,
    dry_run: bool,
) -> None:
    """Update mesocycle."""

    if (
        name is None
        and description is None
        and start_date is None
        and end_date is None
        and status is None
    ):
        raise ValidationError("Provide at least one field to update")

    try:
        dto = UpdateMesocycleInputDTO(
            name=name,
            description=description,
            startDate=_to_date(start_date),
            endDate=_to_date(end_date),
            status=status,
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid update payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateMesocycle",
                "id": str(mesocycle_id),
                "input": payload,
            },
            command="mesocycles update",
        )
        return

    mesocycle: Mesocycle = _run(ctx.mesocycle_service.update(str(mesocycle_id), dto))
    _render(ctx, _mesocycle_to_payload(mesocycle), command="mesocycles update")


@mesocycles.command(name="delete")
@click.argument("mesocycle_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def delete_mesocycle(ctx: CLIContext, mesocycle_id: UUID, force: bool) -> None:
    """Delete mesocycle."""

    if not force:
        raise ValidationError("Use --force to delete mesocycle")

    deleted: bool = _run(ctx.mesocycle_service.delete(str(mesocycle_id)))
    _render(ctx, {"id": str(mesocycle_id), "deleted": deleted}, command="mesocycles delete")


@mesocycles.command(name="add-week")
@click.argument("mesocycle_id", type=click.UUID)
@click.option("--week-number", type=click.IntRange(min=1), required=True)
@click.option(
    "--week-type",
    type=click.Choice(["TRAINING", "DELOAD"], case_sensitive=True),
    required=True,
)
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_week(
    ctx: CLIContext,
    mesocycle_id: UUID,
    week_number: int,
    week_type: str,
    start_date: datetime,
    end_date: datetime,
    dry_run: bool,
) -> None:
    """Add one planning week to a mesocycle."""

    if end_date.date() < start_date.date():
        raise ValidationError("--end-date cannot be earlier than --start-date")

    try:
        dto = AddMesocycleWeekInputDTO(
            weekNumber=week_number,
            weekType=week_type,
            startDate=start_date.date(),
            endDate=end_date.date(),
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid add-week payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "addMesocycleWeek",
                "mesocycle_id": str(mesocycle_id),
                "input": payload,
            },
            command="mesocycles add-week",
        )
        return

    week: MesocycleWeek = _run(ctx.mesocycle_service.add_week(str(mesocycle_id), dto))
    _render(ctx, asdict(week), command="mesocycles add-week")


@mesocycles.command(name="update-week")
@click.argument("week_id", type=click.UUID)
@click.option("--week-number", type=click.IntRange(min=1), default=None)
@click.option(
    "--week-type",
    type=click.Choice(["TRAINING", "DELOAD"], case_sensitive=True),
    default=None,
)
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_week(
    ctx: CLIContext,
    week_id: UUID,
    week_number: int | None,
    week_type: str | None,
    start_date: datetime | None,
    end_date: datetime | None,
    dry_run: bool,
) -> None:
    """Update one mesocycle planning week."""

    if start_date is not None and end_date is not None and end_date.date() < start_date.date():
        raise ValidationError("--end-date cannot be earlier than --start-date")

    try:
        dto = UpdateMesocycleWeekInputDTO(
            weekNumber=week_number,
            weekType=week_type,
            startDate=_to_date(start_date),
            endDate=_to_date(end_date),
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid update-week payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateMesocycleWeek",
                "id": str(week_id),
                "input": payload,
            },
            command="mesocycles update-week",
        )
        return

    week: MesocycleWeek = _run(ctx.mesocycle_service.update_week(str(week_id), dto))
    _render(ctx, asdict(week), command="mesocycles update-week")


@mesocycles.command(name="remove-week")
@click.argument("week_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_week(ctx: CLIContext, week_id: UUID, force: bool) -> None:
    """Remove one planning week from a mesocycle."""

    if not force:
        raise ValidationError("Use --force to remove mesocycle week")

    deleted: bool = _run(ctx.mesocycle_service.remove_week(str(week_id)))
    _render(ctx, {"id": str(week_id), "deleted": deleted}, command="mesocycles remove-week")


@mesocycles.command(name="add-session")
@click.argument("week_id", type=click.UUID)
@click.option("--routine-id", type=click.UUID, default=None)
@click.option("--day-of-week", type=click.IntRange(min=1, max=7), required=True)
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_session(
    ctx: CLIContext,
    week_id: UUID,
    routine_id: UUID | None,
    day_of_week: int,
    date: datetime | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Add one planned session to a mesocycle week."""

    try:
        dto = AddPlannedSessionInputDTO(
            routineId=str(routine_id) if routine_id is not None else None,
            dayOfWeek=day_of_week,
            date=date.date() if date is not None else None,
            notes=notes,
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid add-session payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "addPlannedSession",
                "week_id": str(week_id),
                "input": payload,
            },
            command="mesocycles add-session",
        )
        return

    planned_session: MesocyclePlannedSession = _run(
        ctx.mesocycle_service.add_session(str(week_id), dto)
    )
    _render(ctx, asdict(planned_session), command="mesocycles add-session")


@mesocycles.command(name="update-session")
@click.argument("session_id", type=click.UUID)
@click.option("--routine-id", type=click.UUID, default=None)
@click.option("--day-of-week", type=click.IntRange(min=1, max=7), default=None)
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_session(
    ctx: CLIContext,
    session_id: UUID,
    routine_id: UUID | None,
    day_of_week: int | None,
    date: datetime | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Update one mesocycle planned session."""

    try:
        dto = UpdatePlannedSessionInputDTO(
            routineId=str(routine_id) if routine_id is not None else None,
            dayOfWeek=day_of_week,
            date=date.date() if date is not None else None,
            notes=notes,
        )
    except PydanticValidationError as error:
        message = error.errors()[0]["msg"]
        raise ValidationError(f"Invalid update-session payload: {message}") from error

    payload = dto.model_dump(mode="json", by_alias=True, exclude_none=True)
    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updatePlannedSession",
                "id": str(session_id),
                "input": payload,
            },
            command="mesocycles update-session",
        )
        return

    planned_session: MesocyclePlannedSession = _run(
        ctx.mesocycle_service.update_session(str(session_id), dto)
    )
    _render(ctx, asdict(planned_session), command="mesocycles update-session")


@mesocycles.command(name="remove-session")
@click.argument("session_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_session(ctx: CLIContext, session_id: UUID, force: bool) -> None:
    """Remove one planned session from a mesocycle week."""

    if not force:
        raise ValidationError("Use --force to remove mesocycle planned session")

    deleted: bool = _run(ctx.mesocycle_service.remove_session(str(session_id)))
    _render(
        ctx,
        {"id": str(session_id), "deleted": deleted},
        command="mesocycles remove-session",
    )
