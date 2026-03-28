from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
import time
from urllib.request import Request, urlopen

from conftest import APIRuntime, CLIResult


_RUNTIME_DIRS: list[Path] = []


def _assert_api_health(api_runtime: APIRuntime) -> None:
    request = Request(url=f"{api_runtime.base_url}/health", method="GET")
    with urlopen(request, timeout=3) as response:  # noqa: S310
        assert int(getattr(response, "status", 0)) == 200
        health_payload = json.loads(response.read().decode("utf-8"))
        assert health_payload["status"] == "ok"
        assert health_payload["database"] == "ok"


def _list_items(run_cli: Callable[[list[str]], CLIResult]) -> list[dict[str, object]]:
    result = run_cli(["--json", "exercises", "list"])
    assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"
    payload = json.loads(result.stdout.strip())
    assert payload["success"] is True
    data = payload["data"]
    assert isinstance(data, dict)
    items = data["items"]
    assert isinstance(items, list)
    return items


def _wait_for_backup_artifact(
    backups_dir: Path, timeout_seconds: float = 5.0
) -> list[Path]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        artifacts = [path for path in backups_dir.iterdir() if path.is_file()]
        if artifacts:
            return artifacts
        time.sleep(0.1)
    return []


def test_01_e2e_isolation_seed_and_backup(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    _assert_api_health(api_runtime)
    assert _list_items(run_cli) == []

    create_result = run_cli(
        ["--json", "exercises", "create", "--name", "E2E Isolation Exercise"]
    )
    assert create_result.returncode == 0, (
        f"Create failed with stderr: {create_result.stderr}"
    )
    created_payload = json.loads(create_result.stdout.strip())
    assert created_payload["success"] is True

    assert len(_list_items(run_cli)) == 1

    backup_result = run_cli(["--json", "backup", "trigger"])
    assert backup_result.returncode == 0, (
        f"Backup failed with stderr: {backup_result.stderr}"
    )
    backup_payload = json.loads(backup_result.stdout.strip())
    assert backup_payload["success"] is True
    assert _wait_for_backup_artifact(api_runtime.backups_dir)

    _RUNTIME_DIRS.append(api_runtime.runtime_dir)


def test_02_e2e_starts_clean_and_cleans_previous_runtime(
    api_runtime: APIRuntime, run_cli: Callable[[list[str]], CLIResult]
) -> None:
    _assert_api_health(api_runtime)

    assert _RUNTIME_DIRS, "Expected prior test to record runtime directory"
    previous_runtime_dir = _RUNTIME_DIRS[-1]
    assert api_runtime.runtime_dir != previous_runtime_dir
    assert not previous_runtime_dir.exists()

    assert _list_items(run_cli) == []
    assert list(api_runtime.backups_dir.iterdir()) == []
