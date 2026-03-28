"""GraphQL-backed exercise repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.exercise import Exercise
from workouter_cli.domain.repositories.exercise import ExerciseRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import map_exercise
from workouter_cli.infrastructure.graphql.mutations.exercise import (
    CREATE_EXERCISE,
    DELETE_EXERCISE,
    UPDATE_EXERCISE,
)
from workouter_cli.infrastructure.graphql.queries.exercise import GET_EXERCISE, LIST_EXERCISES


class GraphQLExerciseRepository(ExerciseRepository):
    """Exercise repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        muscle_group_id: str | None = None,
    ) -> tuple[list[Exercise], dict[str, int]]:
        variables = {
            "pagination": {"page": page, "pageSize": page_size},
            "muscleGroupId": muscle_group_id,
        }
        result = await self.client.execute(LIST_EXERCISES, variables)
        payload = result["exercises"]
        items = [map_exercise(item) for item in payload["items"]]
        pagination = {
            "total": int(payload["total"]),
            "page": int(payload["page"]),
            "pageSize": int(payload["pageSize"]),
            "totalPages": int(payload["totalPages"]),
        }
        return items, pagination

    async def get(self, exercise_id: str) -> Exercise:
        result = await self.client.execute(GET_EXERCISE, {"id": exercise_id})
        return map_exercise(result["exercise"])

    async def create(self, payload: dict[str, str | None]) -> Exercise:
        result = await self.client.execute(CREATE_EXERCISE, {"input": payload})
        return map_exercise(result["createExercise"])

    async def update(self, exercise_id: str, payload: dict[str, str | None]) -> Exercise:
        result = await self.client.execute(
            UPDATE_EXERCISE,
            {
                "id": exercise_id,
                "input": payload,
            },
        )
        return map_exercise(result["updateExercise"])

    async def delete(self, exercise_id: str) -> bool:
        result = await self.client.execute(DELETE_EXERCISE, {"id": exercise_id})
        return bool(result["deleteExercise"])
