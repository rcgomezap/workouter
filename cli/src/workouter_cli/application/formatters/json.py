"""JSON output formatter for automation-friendly output."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any


class JsonFormatter:
    """Render payloads as strict, single-line JSON."""

    def format(self, data: Any, command: str) -> str:
        payload = {
            "success": True,
            "data": data,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "command": command,
            },
        }
        return json.dumps(payload, separators=(",", ":"), default=str)
