"""Workout workflow command group."""

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
from workouter_cli.domain.entities.session import Session, SessionSet
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


def _resolve_active_session_id(ctx: CLIContext, session_id: str | None) -> str:
    if session_id is not None:
        return session_id

    sessions, _ = _run(ctx.session_service.list(page=1, page_size=2, status="IN_PROGRESS"))
    if not sessions:
        raise ValidationError("No active session found; provide --session-id")
    if len(sessions) > 1:
        raise ValidationError("Multiple active sessions found; provide --session-id")
    return sessions[0].id


@click.group(name="workout")
def workout() -> None:
    """High-level workout workflow commands."""


@workout.command(name="today")
@click.option("--date", "date_str", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.pass_obj
def workout_today(ctx: CLIContext, date_str: datetime | None) -> None:
    """Show today's planned workout (or a specific date)."""

    target_date = date_str.date() if date_str is not None else None
    day: CalendarDay = _run(ctx.workflow_service.today(target_date=target_date))
    _render(ctx, asdict(day), command="workout today")


@workout.command(name="start")
@click.option("--routine-id", type=str, default=None)
@click.option("--mesocycle-id", type=str, default=None)
@click.option("--notes", type=str, default=None)
@click.option("--date", "date_str", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--dry-run", is_flag=True, help="Validate without creating")
@click.pass_obj
def workout_start(
    ctx: CLIContext,
    routine_id: str | None,
    mesocycle_id: str | None,
    notes: str | None,
    date_str: datetime | None,
    dry_run: bool,
) -> None:
    """Start a workout session from today's plan or explicit routine."""

    if dry_run:
        if routine_id is None:
            raise ValidationError("Missing required flag for dry-run: --routine-id")
        payload: dict[str, object] = {
            "dry_run": True,
            "operations": [
                {
                    "operation": "createSession",
                    "input": {
                        "plannedSessionId": None,
                        "mesocycleId": mesocycle_id,
                        "routineId": routine_id,
                        "notes": notes,
                    },
                },
                {
                    "operation": "startSession",
                    "input": {"id": "$createSession.id"},
                },
            ],
        }
        if date_str is not None:
            payload["date"] = date_str.date().isoformat()
        _render(ctx, payload, command="workout start")
        return

    target_date = date_str.date() if date_str is not None else None
    session: Session = _run(
        ctx.workflow_service.start(
            target_date=target_date,
            routine_id=routine_id,
            mesocycle_id=mesocycle_id,
            notes=notes,
        )
    )
    _render(ctx, asdict(session), command="workout start")


@workout.command(name="log")
@click.option("--session-id", type=str, default=None)
@click.option("--set-id", type=str, default=None)
@click.option("--reps", type=int, default=None)
@click.option("--weight", type=float, default=None)
@click.option("--rir", type=int, default=None)
@click.pass_obj
def workout_log(
    ctx: CLIContext,
    session_id: str | None,
    set_id: str | None,
    reps: int | None,
    weight: float | None,
    rir: int | None,
) -> None:
    """Log set results for an active workout session."""

    if set_id is None:
        raise ValidationError("Missing required flag: --set-id")
    if reps is None:
        raise ValidationError("Missing required flag: --reps")
    if weight is None:
        raise ValidationError("Missing required flag: --weight")

    resolved_session_id = _resolve_active_session_id(ctx, session_id)

    payload: dict[str, int | float | str | None] = {
        "actualReps": reps,
        "actualWeightKg": weight,
        "actualRir": rir,
    }
    logged: SessionSet = _run(ctx.session_service.log_set(set_id=set_id, payload=payload))
    _render(
        ctx,
        {
            "session_id": resolved_session_id,
            "set": asdict(logged),
        },
        command="workout log",
    )


@workout.command(name="complete")
@click.option("--session-id", type=str, default=None)
@click.option("--notes", type=str, default=None)
@click.pass_obj
def workout_complete(ctx: CLIContext, session_id: str | None, notes: str | None) -> None:
    """Complete a workout session."""

    resolved_session_id = _resolve_active_session_id(ctx, session_id)
    if notes is not None:
        _run(ctx.session_service.update(resolved_session_id, {"notes": notes}))
    session: Session = _run(ctx.session_service.complete(resolved_session_id))
    _render(ctx, asdict(session), command="workout complete")
