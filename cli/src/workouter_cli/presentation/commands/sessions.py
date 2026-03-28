"""Sessions command group."""

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
from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet
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


@click.group(name="sessions")
def sessions() -> None:
    """Session lifecycle and set logging commands."""


@sessions.command(name="list")
@click.option("--page", type=int, default=1, show_default=True)
@click.option("--page-size", type=int, default=20, show_default=True)
@click.option(
    "--status",
    type=click.Choice(["PLANNED", "IN_PROGRESS", "COMPLETED"], case_sensitive=True),
    default=None,
)
@click.option("--mesocycle-id", type=click.UUID, default=None)
@click.option("--date-from", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--date-to", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.pass_obj
def list_sessions(
    ctx: CLIContext,
    page: int,
    page_size: int,
    status: str | None,
    mesocycle_id: UUID | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> None:
    """List sessions."""

    items: list[Session]
    pagination: dict[str, int]
    items, pagination = _run(
        ctx.session_service.list(
            page=page,
            page_size=page_size,
            status=status,
            mesocycle_id=str(mesocycle_id) if mesocycle_id is not None else None,
            date_from=date_from.date().isoformat() if date_from is not None else None,
            date_to=date_to.date().isoformat() if date_to is not None else None,
        )
    )
    payload = {
        "items": [asdict(item) for item in items],
        "total": pagination["total"],
        "page": pagination["page"],
        "page_size": pagination["pageSize"],
        "total_pages": pagination["totalPages"],
    }
    _render(ctx, payload, command="sessions list")


@sessions.command(name="get")
@click.argument("session_id", type=click.UUID)
@click.pass_obj
def get_session(ctx: CLIContext, session_id: UUID) -> None:
    """Get one session by ID."""

    session: Session = _run(ctx.session_service.get(str(session_id)))
    _render(ctx, asdict(session), command="sessions get")


@sessions.command(name="create")
@click.option("--planned-session-id", type=click.UUID, default=None)
@click.option("--mesocycle-id", type=click.UUID, default=None)
@click.option("--routine-id", type=click.UUID, default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without creating")
@click.pass_obj
def create_session(
    ctx: CLIContext,
    planned_session_id: UUID | None,
    mesocycle_id: UUID | None,
    routine_id: UUID | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Create session."""

    payload: dict[str, str | None] = {
        "plannedSessionId": str(planned_session_id) if planned_session_id is not None else None,
        "mesocycleId": str(mesocycle_id) if mesocycle_id is not None else None,
        "routineId": str(routine_id) if routine_id is not None else None,
        "notes": notes,
    }
    if dry_run:
        _render(
            ctx,
            {"dry_run": True, "operation": "createSession", "input": payload},
            command="sessions create",
        )
        return

    session: Session = _run(ctx.session_service.create(payload))
    _render(ctx, asdict(session), command="sessions create")


@sessions.command(name="start")
@click.argument("session_id", type=click.UUID)
@click.pass_obj
def start_session(ctx: CLIContext, session_id: UUID) -> None:
    """Start session."""

    session: Session = _run(ctx.session_service.start(str(session_id)))
    _render(ctx, asdict(session), command="sessions start")


@sessions.command(name="complete")
@click.argument("session_id", type=click.UUID)
@click.pass_obj
def complete_session(ctx: CLIContext, session_id: UUID) -> None:
    """Complete session."""

    session: Session = _run(ctx.session_service.complete(str(session_id)))
    _render(ctx, asdict(session), command="sessions complete")


@sessions.command(name="update")
@click.argument("session_id", type=click.UUID)
@click.option("--started-at", type=click.DateTime(), default=None)
@click.option("--completed-at", type=click.DateTime(), default=None)
@click.option(
    "--status",
    type=click.Choice(["PLANNED", "IN_PROGRESS", "COMPLETED"], case_sensitive=True),
    default=None,
)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without updating")
@click.pass_obj
def update_session(
    ctx: CLIContext,
    session_id: UUID,
    started_at: datetime | None,
    completed_at: datetime | None,
    status: str | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Update session."""

    payload: dict[str, str | None] = {}
    if started_at is not None:
        payload["startedAt"] = started_at.isoformat()
    if completed_at is not None:
        payload["completedAt"] = completed_at.isoformat()
    if status is not None:
        payload["status"] = status
    if notes is not None:
        payload["notes"] = notes

    _require_any_update(payload, "Provide at least one field to update")

    if dry_run:
        _render(
            ctx,
            {
                "dry_run": True,
                "operation": "updateSession",
                "id": str(session_id),
                "input": payload,
            },
            command="sessions update",
        )
        return

    session: Session = _run(ctx.session_service.update(str(session_id), payload))
    _render(ctx, asdict(session), command="sessions update")


@sessions.command(name="delete")
@click.argument("session_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def delete_session(ctx: CLIContext, session_id: UUID, force: bool) -> None:
    """Delete session."""

    if not force:
        raise ValidationError("Use --force to delete session")

    deleted: bool = _run(ctx.session_service.delete(str(session_id)))
    _render(ctx, {"id": str(session_id), "deleted": deleted}, command="sessions delete")


@sessions.command(name="add-exercise")
@click.argument("session_id", type=click.UUID)
@click.option("--exercise-id", type=click.UUID, required=True)
@click.option("--order", type=int, required=True)
@click.option("--superset-group", type=int, default=None)
@click.option("--rest-seconds", type=int, default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_session_exercise(
    ctx: CLIContext,
    session_id: UUID,
    exercise_id: UUID,
    order: int,
    superset_group: int | None,
    rest_seconds: int | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Add exercise to a session."""

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
                "operation": "addSessionExercise",
                "session_id": str(session_id),
                "input": payload,
            },
            command="sessions add-exercise",
        )
        return

    session: Session = _run(ctx.session_service.add_exercise(str(session_id), payload))
    _render(ctx, asdict(session), command="sessions add-exercise")


@sessions.command(name="update-exercise")
@click.argument("session_exercise_id", type=click.UUID)
@click.option("--order", type=int, default=None)
@click.option("--superset-group", type=int, default=None)
@click.option("--rest-seconds", type=int, default=None)
@click.option("--notes", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_session_exercise(
    ctx: CLIContext,
    session_exercise_id: UUID,
    order: int | None,
    superset_group: int | None,
    rest_seconds: int | None,
    notes: str | None,
    dry_run: bool,
) -> None:
    """Update one session exercise."""

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
                "operation": "updateSessionExercise",
                "id": str(session_exercise_id),
                "input": payload,
            },
            command="sessions update-exercise",
        )
        return

    session_exercise: SessionExercise = _run(
        ctx.session_service.update_exercise(str(session_exercise_id), payload)
    )
    _render(ctx, asdict(session_exercise), command="sessions update-exercise")


@sessions.command(name="remove-exercise")
@click.argument("session_exercise_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_session_exercise(ctx: CLIContext, session_exercise_id: UUID, force: bool) -> None:
    """Remove one exercise from a session."""

    if not force:
        raise ValidationError("Use --force to remove session exercise")

    deleted: bool = _run(ctx.session_service.remove_exercise(str(session_exercise_id)))
    _render(
        ctx,
        {"id": str(session_exercise_id), "deleted": deleted},
        command="sessions remove-exercise",
    )


@sessions.command(name="add-set")
@click.argument("session_exercise_id", type=click.UUID)
@click.option("--set-number", type=int, required=True)
@click.option(
    "--set-type",
    type=click.Choice(["STANDARD", "DROPSET"], case_sensitive=True),
    required=True,
)
@click.option("--target-reps", type=int, default=None)
@click.option("--target-rir", type=int, default=None)
@click.option("--target-weight", type=float, default=None)
@click.option("--weight-reduction-pct", type=float, default=None)
@click.option("--rest-seconds", type=int, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def add_session_set(
    ctx: CLIContext,
    session_exercise_id: UUID,
    set_number: int,
    set_type: str,
    target_reps: int | None,
    target_rir: int | None,
    target_weight: float | None,
    weight_reduction_pct: float | None,
    rest_seconds: int | None,
    dry_run: bool,
) -> None:
    """Add set to a session exercise."""

    payload: dict[str, object] = {
        "setNumber": set_number,
        "setType": set_type,
    }
    if target_reps is not None:
        payload["targetReps"] = target_reps
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
                "operation": "addSessionSet",
                "session_exercise_id": str(session_exercise_id),
                "input": payload,
            },
            command="sessions add-set",
        )
        return

    session_exercise: SessionExercise = _run(
        ctx.session_service.add_set(str(session_exercise_id), payload)
    )
    _render(ctx, asdict(session_exercise), command="sessions add-set")


@sessions.command(name="update-set")
@click.argument("set_id", type=click.UUID)
@click.option("--set-number", type=int, default=None)
@click.option(
    "--set-type",
    type=click.Choice(["STANDARD", "DROPSET"], case_sensitive=True),
    default=None,
)
@click.option("--target-reps", type=int, default=None)
@click.option("--target-rir", type=int, default=None)
@click.option("--target-weight", type=float, default=None)
@click.option("--weight-reduction-pct", type=float, default=None)
@click.option("--rest-seconds", type=int, default=None)
@click.option("--dry-run", is_flag=True, help="Validate without mutating")
@click.pass_obj
def update_session_set(
    ctx: CLIContext,
    set_id: UUID,
    set_number: int | None,
    set_type: str | None,
    target_reps: int | None,
    target_rir: int | None,
    target_weight: float | None,
    weight_reduction_pct: float | None,
    rest_seconds: int | None,
    dry_run: bool,
) -> None:
    """Update one session set."""

    payload: dict[str, object] = {}
    if set_number is not None:
        payload["setNumber"] = set_number
    if set_type is not None:
        payload["setType"] = set_type
    if target_reps is not None:
        payload["targetReps"] = target_reps
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
                "operation": "updateSessionSet",
                "id": str(set_id),
                "input": payload,
            },
            command="sessions update-set",
        )
        return

    session_set: SessionSet = _run(ctx.session_service.update_set(str(set_id), payload))
    _render(ctx, asdict(session_set), command="sessions update-set")


@sessions.command(name="remove-set")
@click.argument("set_id", type=click.UUID)
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_obj
def remove_session_set(ctx: CLIContext, set_id: UUID, force: bool) -> None:
    """Remove one set from a session exercise."""

    if not force:
        raise ValidationError("Use --force to remove session set")

    deleted: bool = _run(ctx.session_service.remove_set(str(set_id)))
    _render(ctx, {"id": str(set_id), "deleted": deleted}, command="sessions remove-set")


@sessions.command(name="log-set")
@click.argument("set_id", type=click.UUID)
@click.option("--reps", type=int, required=True)
@click.option("--weight", type=float, required=True)
@click.option("--rir", type=int, default=None)
@click.option("--performed-at", type=click.DateTime(), default=None)
@click.pass_obj
def log_set(
    ctx: CLIContext,
    set_id: UUID,
    reps: int,
    weight: float,
    rir: int | None,
    performed_at: datetime | None,
) -> None:
    """Log one set result."""

    payload: dict[str, int | float | str | None] = {
        "actualReps": reps,
        "actualWeightKg": weight,
        "actualRir": rir,
        "performedAt": performed_at.isoformat() if performed_at is not None else None,
    }
    session_set: SessionSet = _run(ctx.session_service.log_set(str(set_id), payload))
    _render(ctx, asdict(session_set), command="sessions log-set")
