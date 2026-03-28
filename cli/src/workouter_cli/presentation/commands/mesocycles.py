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
    CreateMesocycleInputDTO,
    UpdateMesocycleInputDTO,
)
from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.mesocycle import Mesocycle
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
