"""GraphQL-backed muscle group repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.exercise import MuscleGroup
from workouter_cli.domain.repositories.muscle_group import MuscleGroupRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_muscle_group
from workouter_cli.infrastructure.graphql.queries.muscle_group import LIST_MUSCLE_GROUPS


class GraphQLMuscleGroupRepository(MuscleGroupRepository):
    """Muscle group repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def list_all(self) -> list[MuscleGroup]:
        """List all muscle groups (17 predefined groups)."""
        result = await self.client.execute(LIST_MUSCLE_GROUPS, {})
        return [map_muscle_group(item) for item in result["muscleGroups"]]
