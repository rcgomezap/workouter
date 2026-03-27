"""Structured logging setup for CLI runtime."""

from __future__ import annotations

import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog

from workouter_cli.infrastructure.config.schema import Config


def _configure_stdlib_logging(level_name: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level_name, logging.INFO))


def _add_event_key(
    _: Any, __: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    if "event" not in event_dict and "message" in event_dict:
        event_dict["event"] = str(event_dict["message"])
    return event_dict


def setup_logging(config: Config) -> None:
    """Configure structlog to emit logs to stderr only."""

    _configure_stdlib_logging(config.log_level)

    renderer: structlog.types.Processor
    if config.log_level == "DEBUG":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            _add_event_key,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
