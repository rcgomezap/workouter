from datetime import date

import strawberry
from strawberry.types import Info

from app.presentation.graphql.context import Context
from app.presentation.graphql.resolvers.mesocycle import map_planned_session
from app.presentation.graphql.resolvers.session import map_session
from app.presentation.graphql.types.calendar import CalendarDay


def map_calendar_day(d) -> CalendarDay:
    return CalendarDay(
        date=d.date,
        planned_session=map_planned_session(d.planned_session) if d.planned_session else None,
        session=map_session(d.session) if d.session else None,
        is_completed=d.is_completed,
        is_rest_day=d.is_rest_day,
    )


@strawberry.type
class CalendarQuery:
    @strawberry.field
    async def calendar_day(self, info: Info[Context, None], date: date) -> CalendarDay:
        d = await info.context.calendar_service.get_day(date)
        return map_calendar_day(d)

    @strawberry.field
    async def calendar_range(
        self, info: Info[Context, None], start_date: date, end_date: date
    ) -> list[CalendarDay]:
        days = await info.context.calendar_service.get_range(start_date, end_date)
        return [map_calendar_day(d) for d in days]
