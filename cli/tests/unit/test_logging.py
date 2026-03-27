from __future__ import annotations

import io
import logging
from typing import cast

import structlog

from workouter_cli.infrastructure.config.schema import Config
from workouter_cli.presentation.middleware.logging import setup_logging


def _capture_stderr() -> io.StringIO:
    root = logging.getLogger()
    assert root.handlers
    stream = io.StringIO()
    handler = cast(logging.StreamHandler[io.StringIO], root.handlers[0])
    handler.setStream(stream)
    return stream


def test_setup_logging_uses_json_renderer_for_debug() -> None:
    config = Config.model_validate(
        {
            "api_url": "http://localhost:8000/graphql",
            "api_key": "k",
            "timeout": 30,
            "log_level": "DEBUG",
        }
    )

    setup_logging(config)
    stream = _capture_stderr()

    structlog.get_logger().info("debug message", key="value")
    output = stream.getvalue()

    assert '"event": "debug message"' in output
    assert '"key": "value"' in output


def test_setup_logging_uses_console_renderer_for_non_debug() -> None:
    config = Config.model_validate(
        {
            "api_url": "http://localhost:8000/graphql",
            "api_key": "k",
            "timeout": 30,
            "log_level": "INFO",
        }
    )

    setup_logging(config)
    stream = _capture_stderr()

    structlog.get_logger().info("plain message", key="value")
    output = stream.getvalue()

    assert "plain message" in output
    assert "key" in output


def test_logging_does_not_write_to_stdout(capsys) -> None:  # type: ignore[no-untyped-def]
    config = Config.model_validate(
        {
            "api_url": "http://localhost:8000/graphql",
            "api_key": "k",
            "timeout": 30,
            "log_level": "INFO",
        }
    )

    setup_logging(config)
    structlog.get_logger().info("stderr only")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "stderr only" in captured.err
