"""GraphQL-backed routine repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from workouter_cli.domain.repositories.routine import RoutineRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import (
    map_routine,
    map_routine_exercise,
    map_routine_set,
)
from workouter_cli.infrastructure.graphql.mutations.routine import (
    ADD_ROUTINE_EXERCISE,
    ADD_ROUTINE_SET,
    REMOVE_ROUTINE_EXERCISE,
    REMOVE_ROUTINE_SET,
    UPDATE_ROUTINE_EXERCISE,
    UPDATE_ROUTINE_SET,
)


class GraphQLRoutineRepository(RoutineRepository):
    """Routine repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def add_exercise(self, routine_id: str, payload: dict[str, object]) -> Routine:
        result = await self.client.execute(
            ADD_ROUTINE_EXERCISE,
            {"routineId": routine_id, "input": payload},
        )
        return map_routine(result["addRoutineExercise"])

    async def update_exercise(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        result = await self.client.execute(
            UPDATE_ROUTINE_EXERCISE,
            {"id": routine_exercise_id, "input": payload},
        )
        return map_routine_exercise(result["updateRoutineExercise"])

    async def remove_exercise(self, routine_exercise_id: str) -> bool:
        result = await self.client.execute(REMOVE_ROUTINE_EXERCISE, {"id": routine_exercise_id})
        return bool(result["removeRoutineExercise"])

    async def add_set(
        self, routine_exercise_id: str, payload: dict[str, object]
    ) -> RoutineExercise:
        result = await self.client.execute(
            ADD_ROUTINE_SET,
            {"routineExerciseId": routine_exercise_id, "input": payload},
        )
        return map_routine_exercise(result["addRoutineSet"])

    async def update_set(self, set_id: str, payload: dict[str, object]) -> RoutineSet:
        result = await self.client.execute(
            UPDATE_ROUTINE_SET,
            {"id": set_id, "input": payload},
        )
        return map_routine_set(result["updateRoutineSet"])

    async def remove_set(self, set_id: str) -> bool:
        result = await self.client.execute(REMOVE_ROUTINE_SET, {"id": set_id})
        return bool(result["removeRoutineSet"])
