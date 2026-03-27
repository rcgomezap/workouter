"""Factory for choosing output formatter strategy."""

from __future__ import annotations

from workouter_cli.application.formatters.base import Formatter
from workouter_cli.application.formatters.json import JsonFormatter
from workouter_cli.application.formatters.table import TableFormatter


def get_formatter(output_json: bool) -> Formatter:
    """Select formatter based on global JSON output flag."""

    if output_json:
        return JsonFormatter()
    return TableFormatter()
