"""GraphQL-backed calendar repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.calendar import CalendarDay
from workouter_cli.domain.repositories.calendar import CalendarRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_calendar_day
from workouter_cli.infrastructure.graphql.queries.calendar import CALENDAR_DAY, CALENDAR_RANGE


class GraphQLCalendarRepository(CalendarRepository):
    """Calendar repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def day(self, date: str) -> CalendarDay:
        result = await self.client.execute(CALENDAR_DAY, {"date": date})
        return map_calendar_day(result["calendarDay"])

    async def range(self, start_date: str, end_date: str) -> list[CalendarDay]:
        result = await self.client.execute(
            CALENDAR_RANGE,
            {"startDate": start_date, "endDate": end_date},
        )
        return [map_calendar_day(item) for item in result["calendarRange"]]
