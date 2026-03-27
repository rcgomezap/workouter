from rich.table import Table

from workouter_cli.application.formatters.table import TableFormatter


def test_table_formatter_returns_rich_table_for_mapping() -> None:
    formatter = TableFormatter()

    output = formatter.format({"message": "ok"}, command="ping")

    assert isinstance(output, Table)
    assert output.title == "ping"


def test_table_formatter_returns_rich_table_for_list_of_dicts() -> None:
    formatter = TableFormatter()

    output = formatter.format([{"id": "1", "name": "Bench"}], command="exercises list")

    assert isinstance(output, Table)
    assert output.title == "exercises list"
