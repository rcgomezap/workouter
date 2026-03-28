from __future__ import annotations

import json

from click.testing import CliRunner

from workouter_cli.main import cli


def test_schema_command_outputs_valid_json_for_exercises_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["schema", "exercises list"])

    assert result.exit_code == 0
    payload = json.loads(result.output.strip())

    assert payload["command"] == "exercises list"
    assert payload["description"] == "List exercises."

    options = {item["name"] for item in payload["options"]}
    assert "--page" in options
    assert "--muscle-group-id" in options
