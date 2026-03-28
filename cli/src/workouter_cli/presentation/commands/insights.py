"""Insights command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from typing import Any, TypeVar
from uuid import UUID

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    ProgressiveOverloadInsight,
    VolumeInsight,
)
from workouter_cli.domain.entities.session import Session
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


@click.group(name="insights")
def insights() -> None:
    """Training insights commands."""


@insights.command(name="volume")
@click.option("--mesocycle-id", type=click.UUID, required=True)
@click.option("--muscle-group-id", type=click.UUID, default=None)
@click.pass_obj
def volume_insight(
    ctx: CLIContext,
    mesocycle_id: UUID,
    muscle_group_id: UUID | None,
) -> None:
    """Show mesocycle volume insight."""

    insight: VolumeInsight = _run(
        ctx.insight_service.volume(
            mesocycle_id=str(mesocycle_id),
            muscle_group_id=str(muscle_group_id) if muscle_group_id is not None else None,
        )
    )
    _render(ctx, asdict(insight), command="insights volume")


@insights.command(name="intensity")
@click.option("--mesocycle-id", type=click.UUID, required=True)
@click.pass_obj
def intensity_insight(ctx: CLIContext, mesocycle_id: UUID) -> None:
    """Show mesocycle intensity insight."""

    insight: IntensityInsight = _run(ctx.insight_service.intensity(mesocycle_id=str(mesocycle_id)))
    _render(ctx, asdict(insight), command="insights intensity")


@insights.command(name="overload")
@click.option("--mesocycle-id", type=click.UUID, required=True)
@click.option("--exercise-id", type=click.UUID, required=True)
@click.pass_obj
def overload_insight(ctx: CLIContext, mesocycle_id: UUID, exercise_id: UUID) -> None:
    """Show progressive overload insight."""

    insight: ProgressiveOverloadInsight = _run(
        ctx.insight_service.overload(
            mesocycle_id=str(mesocycle_id),
            exercise_id=str(exercise_id),
        )
    )
    _render(ctx, asdict(insight), command="insights overload")


@insights.command(name="history")
@click.option("--exercise-id", type=click.UUID, required=True)
@click.option("--routine-id", type=click.UUID, default=None)
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.pass_obj
def history_insight(
    ctx: CLIContext,
    exercise_id: UUID,
    routine_id: UUID | None,
    page: int,
    page_size: int,
) -> None:
    """Show exercise history insight."""

    items: list[Session]
    pagination: dict[str, int]
    items, pagination = _run(
        ctx.insight_service.history(
            exercise_id=str(exercise_id),
            routine_id=str(routine_id) if routine_id is not None else None,
            page=page,
            page_size=page_size,
        )
    )
    payload = {
        "items": [asdict(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="insights history")
