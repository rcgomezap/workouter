import strawberry
from datetime import date
from strawberry.types import Info
from app.presentation.graphql.context import Context
from app.presentation.graphql.types.calendar import CalendarDay
from app.presentation.graphql.types.mesocycle import PlannedSession
from app.presentation.graphql.types.session import Session

def map_calendar_day(d) -> CalendarDay:
    return CalendarDay(
        date=d.date,
        planned_session=PlannedSession(
            id=d.planned_session.id,
            routine=None, # Simplified
            day_of_week=d.planned_session.day_of_week,
            date=d.planned_session.date,
            notes=d.planned_session.notes
        ) if d.planned_session else None,
        session=Session(
            id=d.session.id,
            planned_session_id=d.session.planned_session_id,
            mesocycle_id=d.session.mesocycle_id,
            routine_id=d.session.routine_id,
            status=d.session.status,
            started_at=d.session.started_at,
            completed_at=d.session.completed_at,
            notes=d.session.notes,
            exercises=[]
        ) if d.session else None,
        is_completed=d.is_completed,
        is_rest_day=d.is_rest_day
    )

@strawberry.type
class CalendarQuery:
    @strawberry.field
    async def calendar_day(self, info: Info[Context, None], date: date) -> CalendarDay:
        d = await info.context.calendar_service.get_day(date)
        return map_calendar_day(d)

    @strawberry.field
    async def calendar_range(
        self, 
        info: Info[Context, None], 
        start_date: date, 
        end_date: date
    ) -> list[CalendarDay]:
        days = await info.context.calendar_service.get_range(start_date, end_date)
        return [map_calendar_day(d) for d in days]
