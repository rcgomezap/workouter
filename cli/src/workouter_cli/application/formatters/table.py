"""Rich table formatter for human-readable output."""

from __future__ import annotations

from typing import Any

from rich.table import Table


class TableFormatter:
    """Render list and mapping payloads as Rich tables."""

    def format(self, data: Any, command: str) -> Table:
        table = Table(title=command)

        if isinstance(data, list):
            if not data:
                table.add_column("result")
                table.add_row("No data")
                return table

            first_row = data[0]
            if isinstance(first_row, dict):
                columns = [str(key) for key in first_row]
                for column in columns:
                    table.add_column(column)
                for item in data:
                    row = [str(item.get(column, "")) for column in columns]
                    table.add_row(*row)
                return table

            table.add_column("value")
            for item in data:
                table.add_row(str(item))
            return table

        if isinstance(data, dict):
            table.add_column("field")
            table.add_column("value")
            for key, value in data.items():
                table.add_row(str(key), str(value))
            return table

        table.add_column("value")
        table.add_row(str(data))
        return table
