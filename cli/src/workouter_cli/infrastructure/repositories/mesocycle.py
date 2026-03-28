"""GraphQL-backed mesocycle repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.mesocycle import Mesocycle
from workouter_cli.domain.repositories.mesocycle import MesocycleRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_mesocycle
from workouter_cli.infrastructure.graphql.mutations.mesocycle import (
    CREATE_MESOCYCLE,
    DELETE_MESOCYCLE,
    UPDATE_MESOCYCLE,
)
from workouter_cli.infrastructure.graphql.queries.mesocycle import (
    GET_MESOCYCLE,
    LIST_MESOCYCLES,
)


class GraphQLMesocycleRepository(MesocycleRepository):
    """Mesocycle repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Mesocycle], dict[str, int]]:
        result = await self.client.execute(
            LIST_MESOCYCLES,
            {
                "pagination": {"page": page, "pageSize": page_size},
                "status": status,
            },
        )
        payload = result["mesocycles"]
        items = [map_mesocycle(item) for item in payload["items"]]
        pagination = {
            "total": int(payload["total"]),
            "page": int(payload["page"]),
            "pageSize": int(payload["pageSize"]),
            "totalPages": int(payload["totalPages"]),
        }
        return items, pagination

    async def get(self, mesocycle_id: str) -> Mesocycle:
        result = await self.client.execute(GET_MESOCYCLE, {"id": mesocycle_id})
        return map_mesocycle(result["mesocycle"])

    async def create(self, payload: dict[str, str]) -> Mesocycle:
        result = await self.client.execute(CREATE_MESOCYCLE, {"input": payload})
        return map_mesocycle(result["createMesocycle"])

    async def update(self, mesocycle_id: str, payload: dict[str, str]) -> Mesocycle:
        result = await self.client.execute(
            UPDATE_MESOCYCLE,
            {
                "id": mesocycle_id,
                "input": payload,
            },
        )
        return map_mesocycle(result["updateMesocycle"])

    async def delete(self, mesocycle_id: str) -> bool:
        result = await self.client.execute(DELETE_MESOCYCLE, {"id": mesocycle_id})
        return bool(result["deleteMesocycle"])
