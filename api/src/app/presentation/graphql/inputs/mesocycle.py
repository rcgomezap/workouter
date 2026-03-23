from typing import Optional
from uuid import UUID
from datetime import date
import strawberry
from app.presentation.graphql.types.enums import MesocycleStatus, WeekType

@strawberry.input
class CreateMesocycleInput:
    name: str
    description: Optional[str] = None
    start_date: date

@strawberry.input
class UpdateMesocycleInput:
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[MesocycleStatus] = None

@strawberry.input
class AddMesocycleWeekInput:
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date

@strawberry.input
class UpdateMesocycleWeekInput:
    week_number: Optional[int] = None
    week_type: Optional[WeekType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

@strawberry.input
class AddPlannedSessionInput:
    routine_id: Optional[UUID] = None
    day_of_week: int
    date: date
    notes: Optional[str] = None

@strawberry.input
class UpdatePlannedSessionInput:
    routine_id: Optional[UUID] = None
    day_of_week: Optional[int] = None
    date: Optional[date] = None
    notes: Optional[str] = None
