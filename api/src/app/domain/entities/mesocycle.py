from uuid import UUID
from datetime import date
from pydantic import Field
from app.domain.entities.common import TimestampedEntity, BaseEntity
from app.domain.entities.routine import Routine
from app.domain.enums import MesocycleStatus, WeekType


class PlannedSession(BaseEntity):
    mesocycle_week_id: UUID | None = None
    routine: Routine | None = None
    day_of_week: int
    date: date
    notes: str | None = None


class MesocycleWeek(BaseEntity):
    mesocycle_id: UUID | None = None
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date
    planned_sessions: list[PlannedSession] = Field(default_factory=list)


class Mesocycle(TimestampedEntity):
    name: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    status: MesocycleStatus = MesocycleStatus.PLANNED
    weeks: list[MesocycleWeek] = Field(default_factory=list)
