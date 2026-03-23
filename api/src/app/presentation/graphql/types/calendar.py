from datetime import date
import strawberry
from app.presentation.graphql.types.mesocycle import PlannedSession
from app.presentation.graphql.types.session import Session

@strawberry.type
class CalendarDay:
    date: date
    planned_session: PlannedSession | None
    session: Session | None
    is_completed: bool
    is_rest_day: bool
