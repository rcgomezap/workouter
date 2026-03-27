from workouter_cli.application.formatters.factory import get_formatter
from workouter_cli.application.formatters.json import JsonFormatter
from workouter_cli.application.formatters.table import TableFormatter


def test_factory_returns_json_formatter_when_json_enabled() -> None:
    formatter = get_formatter(output_json=True)

    assert isinstance(formatter, JsonFormatter)


def test_factory_returns_table_formatter_by_default() -> None:
    formatter = get_formatter(output_json=False)

    assert isinstance(formatter, TableFormatter)
