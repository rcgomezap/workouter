"""GraphQL-backed bodyweight repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.bodyweight import BodyweightLog
from workouter_cli.domain.repositories.bodyweight import BodyweightRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_bodyweight_log
from workouter_cli.infrastructure.graphql.mutations.bodyweight import (
    DELETE_BODYWEIGHT_LOG,
    LOG_BODYWEIGHT,
    UPDATE_BODYWEIGHT_LOG,
)
from workouter_cli.infrastructure.graphql.queries.bodyweight import LIST_BODYWEIGHT_LOGS


class GraphQLBodyweightRepository(BodyweightRepository):
    """Bodyweight repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[BodyweightLog], dict[str, int]]:
        variables = {
            "pagination": {"page": page, "pageSize": page_size},
            "dateFrom": date_from,
            "dateTo": date_to,
        }
        result = await self.client.execute(LIST_BODYWEIGHT_LOGS, variables)
        payload = result["bodyweightLogs"]
        items = [map_bodyweight_log(item) for item in payload["items"]]
        pagination = {
            "total": int(payload["total"]),
            "page": int(payload["page"]),
            "pageSize": int(payload["pageSize"]),
            "totalPages": int(payload["totalPages"]),
        }
        return items, pagination

    async def log(self, payload: dict[str, str | float | None]) -> BodyweightLog:
        result = await self.client.execute(LOG_BODYWEIGHT, {"input": payload})
        return map_bodyweight_log(result["logBodyweight"])

    async def update(
        self,
        bodyweight_log_id: str,
        payload: dict[str, str | float | None],
    ) -> BodyweightLog:
        result = await self.client.execute(
            UPDATE_BODYWEIGHT_LOG,
            {"id": bodyweight_log_id, "input": payload},
        )
        return map_bodyweight_log(result["updateBodyweightLog"])

    async def delete(self, bodyweight_log_id: str) -> bool:
        result = await self.client.execute(DELETE_BODYWEIGHT_LOG, {"id": bodyweight_log_id})
        return bool(result["deleteBodyweightLog"])
