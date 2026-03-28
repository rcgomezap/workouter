"""GraphQL-backed insights repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.insight import (
    IntensityInsight,
    ProgressiveOverloadInsight,
    VolumeInsight,
)
from workouter_cli.domain.entities.session import Session
from workouter_cli.domain.repositories.insight import InsightRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import (
    map_intensity_insight,
    map_progressive_overload_insight,
    map_session,
    map_volume_insight,
)
from workouter_cli.infrastructure.graphql.queries.insight import (
    EXERCISE_HISTORY,
    MESOCYCLE_INTENSITY_INSIGHT,
    MESOCYCLE_VOLUME_INSIGHT,
    PROGRESSIVE_OVERLOAD_INSIGHT,
)


class GraphQLInsightRepository(InsightRepository):
    """Insight repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def volume(self, mesocycle_id: str, muscle_group_id: str | None = None) -> VolumeInsight:
        result = await self.client.execute(
            MESOCYCLE_VOLUME_INSIGHT,
            {"mesocycleId": mesocycle_id, "muscleGroupId": muscle_group_id},
        )
        return map_volume_insight(result["mesocycleVolumeInsight"])

    async def intensity(self, mesocycle_id: str) -> IntensityInsight:
        result = await self.client.execute(
            MESOCYCLE_INTENSITY_INSIGHT,
            {"mesocycleId": mesocycle_id},
        )
        return map_intensity_insight(result["mesocycleIntensityInsight"])

    async def overload(self, mesocycle_id: str, exercise_id: str) -> ProgressiveOverloadInsight:
        result = await self.client.execute(
            PROGRESSIVE_OVERLOAD_INSIGHT,
            {"mesocycleId": mesocycle_id, "exerciseId": exercise_id},
        )
        return map_progressive_overload_insight(result["progressiveOverloadInsight"])

    async def history(
        self,
        exercise_id: str,
        routine_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Session], dict[str, int]]:
        variables = {
            "exerciseId": exercise_id,
            "routineId": routine_id,
            "pagination": {"page": page, "pageSize": page_size},
        }
        result = await self.client.execute(EXERCISE_HISTORY, variables)
        payload = result["exerciseHistory"]
        items = [map_session(item) for item in payload["items"]]
        pagination = {
            "total": int(payload["total"]),
            "page": int(payload["page"]),
            "pageSize": int(payload["pageSize"]),
            "totalPages": int(payload["totalPages"]),
        }
        return items, pagination
