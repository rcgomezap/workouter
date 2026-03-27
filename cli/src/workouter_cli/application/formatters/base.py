"""Formatter strategy protocol used by presentation commands."""

from __future__ import annotations

from typing import Any, Protocol

from rich.table import Table

FormatterOutput = str | Table


class Formatter(Protocol):
    """Contract for command output formatters."""

    def format(self, data: Any, command: str) -> FormatterOutput:
        """Format command payload for display."""
