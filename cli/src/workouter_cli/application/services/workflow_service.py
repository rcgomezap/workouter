"""Workflow application service."""

from __future__ import annotations

from datetime import UTC, date, datetime

from workouter_cli.domain.entities.calendar import CalendarDay
from workouter_cli.domain.entities.session import Session
from workouter_cli.domain.exceptions import ValidationError
from workouter_cli.domain.repositories.calendar import CalendarRepository
from workouter_cli.domain.repositories.session import SessionRepository


class WorkflowService:
    """High-level workflow orchestration across repositories."""

    def __init__(
        self,
        calendar_repository: CalendarRepository,
        session_repository: SessionRepository,
    ) -> None:
        self.calendar_repository = calendar_repository
        self.session_repository = session_repository

    async def today(self, target_date: date | None = None) -> CalendarDay:
        effective_date = target_date or datetime.now(UTC).date()
        return await self.calendar_repository.day(effective_date.isoformat())

    async def start(
        self,
        target_date: date | None = None,
        routine_id: str | None = None,
        mesocycle_id: str | None = None,
        notes: str | None = None,
    ) -> Session:
        calendar_day = await self.today(target_date)

        selected_routine_id = routine_id
        if selected_routine_id is None and calendar_day.planned_session is not None:
            selected_routine_id = calendar_day.planned_session.routine_id

        if selected_routine_id is None:
            msg = "No planned routine found for date; provide --routine-id"
            raise ValidationError(msg)

        create_input = {
            "plannedSessionId": (
                calendar_day.planned_session.id
                if calendar_day.planned_session is not None
                else None
            ),
            "mesocycleId": mesocycle_id,
            "routineId": selected_routine_id,
            "notes": notes,
        }
        created = await self.session_repository.create(create_input)
        return await self.session_repository.start(created.id)
