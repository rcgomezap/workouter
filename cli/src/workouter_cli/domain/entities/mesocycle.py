"""Mesocycle domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MesocyclePlannedSession:
    """Planned session details nested under a mesocycle week."""

    id: str
    routine_id: str | None
    routine_name: str | None
    day_of_week: int
    date: str
    notes: str | None


@dataclass(slots=True, frozen=True)
class MesocycleWeek:
    """Mesocycle week planning details."""

    id: str
    week_number: int
    week_type: str
    start_date: str
    end_date: str
    planned_sessions: tuple[MesocyclePlannedSession, ...]


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
