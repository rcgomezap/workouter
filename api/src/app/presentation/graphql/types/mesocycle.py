from datetime import date
from uuid import UUID

import strawberry

from app.presentation.graphql.types.enums import MesocycleStatus, WeekType
from app.presentation.graphql.types.routine import Routine


@strawberry.type
class PlannedSession:
    id: UUID
    routine: Routine | None
    day_of_week: int
    date: date
    notes: str | None


@strawberry.type
class MesocycleWeek:
    id: UUID
    week_number: int
    week_type: WeekType
    start_date: date
    end_date: date
    planned_sessions: list[PlannedSession]


@strawberry.type
class Mesocycle:
    id: UUID
    name: str
    description: str | None
    start_date: date
    end_date: date | None
    status: MesocycleStatus
    weeks: list[MesocycleWeek]


@strawberry.type
class PaginatedMesocycles:
    items: list[Mesocycle]
    total: int
    page: int
    page_size: int
    total_pages: int
