"""Global CLI error handling helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import NoReturn

import click
from rich.console import Console

from workouter_cli.domain.exceptions import CLIError, NetworkError


def _build_error_payload(code: str, message: str, command: str) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "command": command,
        },
    }


def handle_cli_error(error: CLIError, output_json: bool, command: str) -> NoReturn:
    """Render a known CLIError and terminate with semantic code."""

    if output_json:
        payload = _build_error_payload(code=error.code, message=str(error), command=command)
        click.echo(json.dumps(payload, separators=(",", ":"), default=str))
    else:
        console = Console(stderr=True)
        console.print(f"[bold red]Error:[/bold red] {error}")

    raise click.exceptions.Exit(int(error.exit_code)) from error


def handle_unexpected_error(error: Exception, output_json: bool, command: str) -> NoReturn:
    """Render an unexpected exception as internal/network failure."""

    wrapped = NetworkError(message=str(error), code="INTERNAL_ERROR")
    handle_cli_error(wrapped, output_json=output_json, command=command)
