import datetime
from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.application.dto.pagination import PaginatedResult
from app.application.dto.routine import RoutineDTO
from app.domain.enums import MesocycleStatus, WeekType


class PlannedSessionDTO(BaseModel):
    id: UUID
    routine: RoutineDTO | None = None
    day_of_week: int
    date: datetime.date
    notes: str | None = None


class MesocycleWeekDTO(BaseModel):
    id: UUID
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date
    planned_sessions: list[PlannedSessionDTO]


class MesocycleDTO(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    status: MesocycleStatus
    weeks: list[MesocycleWeekDTO]


class CreateMesocycleInput(BaseModel):
    name: str
    description: str | None = None
    start_date: date


class UpdateMesocycleInput(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: MesocycleStatus | None = None


class AddMesocycleWeekInput(BaseModel):
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date


class UpdateMesocycleWeekInput(BaseModel):
    week_number: int | None = None
    week_type: WeekType | None = None
    start_date: date | None = None
    end_date: date | None = None


class AddPlannedSessionInput(BaseModel):
    routine_id: UUID | None = None
    day_of_week: int
    date: datetime.date | None = None
    notes: str | None = None


class UpdatePlannedSessionInput(BaseModel):
    routine_id: UUID | None = None
    day_of_week: int | None = None
    date: datetime.date | None = None
    notes: str | None = None


class PaginatedMesocycles(PaginatedResult[MesocycleDTO]):
    pass
