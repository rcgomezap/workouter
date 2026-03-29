"""Muscle groups command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from typing import Any, TypeVar

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.exercise import MuscleGroup
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


def _muscle_group_to_payload(muscle_group: MuscleGroup) -> dict[str, object]:
    return asdict(muscle_group)


@click.group(name="muscle-groups")
def muscle_groups() -> None:
    """Muscle group commands."""


@muscle_groups.command(name="list")
@click.pass_obj
def list_muscle_groups(ctx: CLIContext) -> None:
    """List all muscle groups (17 predefined)."""

    muscle_groups_list: list[MuscleGroup] = _run(ctx.muscle_group_service.list_all())
    payload = [_muscle_group_to_payload(mg) for mg in muscle_groups_list]
    _render(ctx, payload, command="muscle-groups list")
