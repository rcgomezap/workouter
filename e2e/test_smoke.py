from __future__ import annotations

import json
from collections.abc import Callable
from urllib.request import Request, urlopen

from conftest import APIRuntime, CLIResult


def test_api_and_cli_smoke(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    request = Request(url=f"{api_runtime.base_url}/health", method="GET")
    with urlopen(request, timeout=3) as response:  # noqa: S310
        assert int(getattr(response, "status", 0)) == 200
        health_payload = json.loads(response.read().decode("utf-8"))
        assert health_payload["status"] == "ok"
        assert health_payload["database"] == "ok"

    result = run_cli(["--json", "exercises", "list"])
    assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"

    payload = json.loads(result.stdout.strip())
    assert payload["success"] is True
    assert isinstance(payload["data"], dict)
    assert "items" in payload["data"]
    assert "metadata" in payload
    assert payload["metadata"]["command"] == "exercises list"
