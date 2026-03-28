"""Bodyweight command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Mapping
from dataclasses import asdict
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.bodyweight import BodyweightLog
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


@click.group(name="bodyweight")
def bodyweight() -> None:
    """Bodyweight logging commands."""


@bodyweight.command(name="list")
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.option("--date-from", type=click.DateTime(), default=None)
@click.option("--date-to", type=click.DateTime(), default=None)
@click.pass_obj
def list_bodyweight(
    ctx: CLIContext,
    page: int,
    page_size: int,
    date_from: datetime | None,
    date_to: datetime | None,
) -> None:
    """List bodyweight logs."""

    items: list[BodyweightLog]
    pagination: dict[str, int]
    items, pagination = _run(
        ctx.bodyweight_service.list(
            page=page,
            page_size=page_size,
            date_from=date_from.isoformat() if date_from is not None else None,
            date_to=date_to.isoformat() if date_to is not None else None,
        )
    )
    payload = {
        "items": [asdict(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="bodyweight list")


@bodyweight.command(name="log")
@click.option("--weight", type=float, required=True)
@click.option("--recorded-at", type=click.DateTime(), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def log_bodyweight(
    ctx: CLIContext,
    weight: float,
    recorded_at: datetime | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Log bodyweight."""

    payload: dict[str, str | float | None] = {
        "weightKg": weight,
        "recordedAt": recorded_at.isoformat() if recorded_at is not None else None,
        "notes": notes,
    }

    if dry_run:
        _render(
            ctx,
            {"dry_run": True, "operation": "logBodyweight", "input": payload},
            command="bodyweight log",
        )
        return

    created: BodyweightLog = _run(ctx.bodyweight_service.log(payload))
    _render(ctx, asdict(created), command="bodyweight log")


@bodyweight.command(name="update")
@click.argument("bodyweight_log_id", type=click.UUID)
@click.option("--weight", type=float, default=None)
@click.option("--recorded-at", type=click.DateTime(), default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_bodyweight(
    ctx: CLIContext,
    bodyweight_log_id: UUID,
    weight: float | None,
    recorded_at: datetime | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Update one bodyweight log."""

    payload: dict[str, str | float | None] = {}
    if weight is not None:
        payload["weightKg"] = weight
    if recorded_at is not None:
        payload["recordedAt"] = recorded_at.isoformat()
    if notes is not None:
        payload["notes"] = notes

    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateBodyweightLog",
                "id": str(bodyweight_log_id),
                "input": payload,
            },
            command="bodyweight update",
        )
        return

    updated: BodyweightLog = _run(ctx.bodyweight_service.update(str(bodyweight_log_id), payload))
    _render(ctx, asdict(updated), command="bodyweight update")


@bodyweight.command(name="delete")
@click.argument("bodyweight_log_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def delete_bodyweight(ctx: CLIContext, bodyweight_log_id: UUID, force: bool) -> None:
    """Delete one bodyweight log."""

    if not force:
        raise ValidationError("Use --force to delete bodyweight log")

    deleted: bool = _run(ctx.bodyweight_service.delete(str(bodyweight_log_id)))
    _render(
        ctx,
        {"id": str(bodyweight_log_id), "deleted": deleted},
        command="bodyweight delete",
    )
