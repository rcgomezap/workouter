"""Calendar command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from datetime import datetime
from typing import Any, TypeVar

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.calendar import CalendarDay
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


@click.group(name="calendar")
def calendar() -> None:
    """Calendar planning commands."""


@calendar.command(name="day")
@click.option("--date", "date_str", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.pass_obj
def calendar_day(ctx: CLIContext, date_str: datetime) -> None:
    """Show one calendar day."""

    day: CalendarDay = _run(ctx.calendar_service.day(date_str.date().isoformat()))
    _render(ctx, asdict(day), command="calendar day")


@calendar.command(name="range")
@click.option("--start-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--end-date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.pass_obj
def calendar_range(ctx: CLIContext, start_date: datetime, end_date: datetime) -> None:
    """Show calendar range."""

    days: list[CalendarDay] = _run(
        ctx.calendar_service.range(
            start_date.date().isoformat(),
            end_date.date().isoformat(),
        )
    )
    _render(ctx, [asdict(day) for day in days], command="calendar range")
