"""Backup command group."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import asdict
from typing import Any, TypeVar

import click
from rich.console import Console

from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.domain.entities.backup import BackupResult
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


@click.group(name="backup")
def backup() -> None:
    """Backup management commands."""


@backup.command(name="trigger")
@click.pass_obj
def trigger_backup(ctx: CLIContext) -> None:
    """Trigger database backup."""

    result: BackupResult = _run(ctx.backup_service.trigger())
    _render(ctx, asdict(result), command="backup trigger")
