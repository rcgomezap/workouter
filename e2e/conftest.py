from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
API_DIR = REPO_ROOT / "api"
CLI_DIR = REPO_ROOT / "cli"


@dataclass(frozen=True)
class APIRuntime:
    base_url: str
    graphql_url: str
    api_key: str
    runtime_dir: Path
    database_path: Path
    backups_dir: Path
    log_path: Path


@dataclass(frozen=True)
class CLIResult:
    returncode: int
    stdout: str
    stderr: str


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _write_api_config(
    target: Path, port: int, api_key: str, data_dir: Path, backups_dir: Path
) -> None:
    target.write_text(
        "\n".join(
            [
                "server:",
                '  host: "127.0.0.1"',
                f"  port: {port}",
                "  debug: false",
                "database:",
                f'  url: "sqlite+aiosqlite:///{(data_dir / "e2e.sqlite").as_posix()}"',
                "  echo: false",
                "auth:",
                f'  api_key: "{api_key}"',
                "logging:",
                '  level: "INFO"',
                '  format: "json"',
                "  file: null",
                "backup:",
                "  enabled: true",
                f'  directory: "{backups_dir.as_posix()}"',
                "  scheduled:",
                "    enabled: false",
                "    frequency_hours: 24",
                "  max_backups: 5",
                "pagination:",
                "  default_page_size: 20",
                "  max_page_size: 100",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _read_log(log_path: Path) -> str:
    if not log_path.exists():
        return "<missing log file>"
    return log_path.read_text(encoding="utf-8", errors="replace")


def _wait_for_health(
    url: str,
    process: subprocess.Popen[str],
    log_path: Path,
    timeout_seconds: float = 40.0,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            logs = _read_log(log_path)
            raise RuntimeError(
                "API process exited before /health became ready. "
                f"Exit code: {process.returncode}\n\nCaptured logs:\n{logs}"
            )

        request = Request(url=url, method="GET")
        try:
            with urlopen(request, timeout=1.5) as response:  # noqa: S310
                status = int(getattr(response, "status", 0))
                if status == 200:
                    body = response.read().decode("utf-8")
                    payload = json.loads(body)
                    if payload.get("status") == "ok":
                        return
        except (URLError, TimeoutError, json.JSONDecodeError):
            pass

        time.sleep(0.25)

    logs = _read_log(log_path)
    raise RuntimeError(
        "Timed out waiting for API /health readiness. "
        f"Waited {timeout_seconds:.1f}s\n\nCaptured logs:\n{logs}"
    )


@pytest.fixture
def api_runtime() -> Iterator[APIRuntime]:
    with tempfile.TemporaryDirectory(prefix="workouter-e2e-") as runtime_dir_str:
        runtime_dir = Path(runtime_dir_str)
        data_dir = runtime_dir / "data"
        backups_dir = runtime_dir / "backups"
        data_dir.mkdir(parents=True, exist_ok=True)
        backups_dir.mkdir(parents=True, exist_ok=True)

        port = _get_free_port()
        api_key = f"e2e-key-{port}"
        config_path = runtime_dir / "config.e2e.yaml"
        log_path = runtime_dir / "api.log"
        database_path = data_dir / "e2e.sqlite"
        _write_api_config(config_path, port, api_key, data_dir, backups_dir)

        env = os.environ.copy()
        env["CONFIG_PATH"] = str(config_path)
        env["PYTHONPATH"] = "src"

        with log_path.open("w", encoding="utf-8") as log_file:
            process: subprocess.Popen[str] = subprocess.Popen(
                [
                    "uv",
                    "run",
                    "uvicorn",
                    "app.main:create_app",
                    "--factory",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                ],
                cwd=API_DIR,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
            )

        base_url = f"http://127.0.0.1:{port}"

        try:
            _wait_for_health(
                url=f"{base_url}/health", process=process, log_path=log_path
            )
            yield APIRuntime(
                base_url=base_url,
                graphql_url=f"{base_url}/graphql",
                api_key=api_key,
                runtime_dir=runtime_dir,
                database_path=database_path,
                backups_dir=backups_dir,
                log_path=log_path,
            )
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


@pytest.fixture
def run_cli(api_runtime: APIRuntime) -> Callable[[list[str]], CLIResult]:
    def _runner(args: list[str]) -> CLIResult:
        env = os.environ.copy()
        env["WORKOUTER_API_URL"] = api_runtime.graphql_url
        env["WORKOUTER_API_KEY"] = api_runtime.api_key
        env["WORKOUTER_CLI_TIMEOUT"] = "30"
        env["WORKOUTER_CLI_LOG_LEVEL"] = "INFO"

        completed = subprocess.run(  # noqa: S603
            ["uv", "run", "workouter-cli", *args],
            cwd=CLI_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        return CLIResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    return _runner
