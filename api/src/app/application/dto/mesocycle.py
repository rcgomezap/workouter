from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel
from app.domain.enums import MesocycleStatus, WeekType
from app.application.dto.routine import RoutineDTO
from app.application.dto.pagination import PaginatedResult

class PlannedSessionDTO(BaseModel):
    id: UUID
    routine: Optional[RoutineDTO] = None
    day_of_week: int
    date: date
    notes: Optional[str] = None

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
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    status: MesocycleStatus
    weeks: list[MesocycleWeekDTO]

class CreateMesocycleInput(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date

class UpdateMesocycleInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[MesocycleStatus] = None

class AddMesocycleWeekInput(BaseModel):
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date

class UpdateMesocycleWeekInput(BaseModel):
    week_number: Optional[int] = None
    week_type: Optional[WeekType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class AddPlannedSessionInput(BaseModel):
    routine_id: Optional[UUID] = None
    day_of_week: int
    date: date
    notes: Optional[str] = None

class UpdatePlannedSessionInput(BaseModel):
    routine_id: Optional[UUID] = None
    day_of_week: Optional[int] = None
    date: Optional[date] = None
    notes: Optional[str] = None

class PaginatedMesocycles(PaginatedResult[MesocycleDTO]):
    pass
