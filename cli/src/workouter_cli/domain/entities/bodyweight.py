"""Bodyweight domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BodyweightLog:
    """Single bodyweight measurement log."""

    id: str
    weight_kg: float
    recorded_at: str
    notes: str | None
    created_at: str
