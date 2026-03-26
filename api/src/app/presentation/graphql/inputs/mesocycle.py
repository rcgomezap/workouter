from datetime import date
from uuid import UUID

import strawberry

from app.presentation.graphql.types.enums import MesocycleStatus, WeekType


@strawberry.input
class CreateMesocycleInput:
    name: str
    description: str | None = None
    start_date: date


@strawberry.input
class UpdateMesocycleInput:
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: MesocycleStatus | None = None


@strawberry.input
class AddMesocycleWeekInput:
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date


@strawberry.input
class UpdateMesocycleWeekInput:
    week_number: int | None = None
    week_type: WeekType | None = None
    start_date: date | None = None
    end_date: date | None = None


@strawberry.input
class AddPlannedSessionInput:
    routine_id: UUID | None = None
    day_of_week: int
    date: date | None = None
    notes: str | None = None


@strawberry.input
class UpdatePlannedSessionInput:
    routine_id: UUID | None = None
    day_of_week: int | None = None
    date: date | None = None
    notes: str | None = None
