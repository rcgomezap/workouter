"""Calendar domain entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PlannedSession:
    """Planned session details for a calendar day."""

    id: str
    routine_id: str | None
    routine_name: str | None
    day_of_week: int
    date: str
    notes: str | None


@dataclass(slots=True, frozen=True)
class CalendarDay:
    """Calendar day aggregate used by workflow commands."""

    date: str
    planned_session: PlannedSession | None
    session_id: str | None
    is_completed: bool
    is_rest_day: bool
