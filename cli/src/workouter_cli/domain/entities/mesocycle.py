"""Mesocycle domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MesocycleWeek:
    """Mesocycle week planning details."""

    id: str
    week_number: int
    week_type: str
    start_date: str
    end_date: str


@dataclass(slots=True, frozen=True)
class Mesocycle:
    """Mesocycle aggregate root."""

    id: str
    name: str
    description: str | None
    start_date: str
    end_date: str | None
    status: str
    weeks: tuple[MesocycleWeek, ...]
