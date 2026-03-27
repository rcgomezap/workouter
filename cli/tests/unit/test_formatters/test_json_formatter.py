import json

from workouter_cli.application.formatters.json import JsonFormatter


def test_json_formatter_outputs_single_line_json() -> None:
    formatter = JsonFormatter()

    output = formatter.format({"message": "ok"}, command="ping")

    assert "\n" not in output
    payload = json.loads(output)
    assert payload["success"] is True
    assert payload["data"] == {"message": "ok"}
    assert payload["metadata"]["command"] == "ping"
    assert "timestamp" in payload["metadata"]
