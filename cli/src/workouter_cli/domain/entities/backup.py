"""Backup domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BackupResult:
    """Backup trigger result payload."""

    success: bool
    filename: str | None
    size_bytes: int | None
    created_at: str
