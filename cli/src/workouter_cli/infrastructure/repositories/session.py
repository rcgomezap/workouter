"""GraphQL-backed session repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.session import Session, SessionExercise, SessionSet
from workouter_cli.domain.repositories.session import SessionRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import (
    map_session,
    map_session_exercise,
    map_session_set,
)
from workouter_cli.infrastructure.graphql.mutations.session import (
    ADD_SESSION_EXERCISE,
    ADD_SESSION_SET,
    COMPLETE_SESSION,
    CREATE_SESSION,
    DELETE_SESSION,
    LOG_SET_RESULT,
    REMOVE_SESSION_EXERCISE,
    REMOVE_SESSION_SET,
    START_SESSION,
    UPDATE_SESSION_EXERCISE,
    UPDATE_SESSION,
    UPDATE_SESSION_SET,
)
from workouter_cli.infrastructure.graphql.queries.session import GET_SESSION, LIST_SESSIONS


class GraphQLSessionRepository(SessionRepository):
    """Session repository using GraphQL API operations."""

    def __init__(self, client: GraphQLClient) -> None:
        self.client = client

    async def create(self, payload: dict[str, str | None]) -> Session:
        result = await self.client.execute(CREATE_SESSION, {"input": payload})
        return map_session(result["createSession"])

    async def start(self, session_id: str) -> Session:
        result = await self.client.execute(START_SESSION, {"id": session_id})
        return map_session(result["startSession"])

    async def complete(self, session_id: str) -> Session:
        result = await self.client.execute(COMPLETE_SESSION, {"id": session_id})
        return map_session(result["completeSession"])

    async def update(self, session_id: str, payload: dict[str, str | None]) -> Session:
        result = await self.client.execute(UPDATE_SESSION, {"id": session_id, "input": payload})
        return map_session(result["updateSession"])

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        mesocycle_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[Session], dict[str, int]]:
        variables = {
            "pagination": {"page": page, "pageSize": page_size},
            "status": status,
            "mesocycleId": mesocycle_id,
            "dateFrom": date_from,
            "dateTo": date_to,
        }
        result = await self.client.execute(LIST_SESSIONS, variables)
        payload = result["sessions"]
        items = [map_session(item) for item in payload["items"]]
        pagination = {
            "total": int(payload["total"]),
            "page": int(payload["page"]),
            "pageSize": int(payload["pageSize"]),
            "totalPages": int(payload["totalPages"]),
        }
        return items, pagination

    async def get(self, session_id: str) -> Session:
        result = await self.client.execute(GET_SESSION, {"id": session_id})
        return map_session(result["session"])

    async def delete(self, session_id: str) -> bool:
        result = await self.client.execute(DELETE_SESSION, {"id": session_id})
        return bool(result["deleteSession"])

    async def add_exercise(self, session_id: str, payload: dict[str, object]) -> Session:
        result = await self.client.execute(
            ADD_SESSION_EXERCISE,
            {"sessionId": session_id, "input": payload},
        )
        return map_session(result["addSessionExercise"])

    async def update_exercise(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        result = await self.client.execute(
            UPDATE_SESSION_EXERCISE,
            {"id": session_exercise_id, "input": payload},
        )
        return map_session_exercise(result["updateSessionExercise"])

    async def remove_exercise(self, session_exercise_id: str) -> bool:
        result = await self.client.execute(REMOVE_SESSION_EXERCISE, {"id": session_exercise_id})
        return bool(result["removeSessionExercise"])

    async def add_set(
        self, session_exercise_id: str, payload: dict[str, object]
    ) -> SessionExercise:
        result = await self.client.execute(
            ADD_SESSION_SET,
            {"sessionExerciseId": session_exercise_id, "input": payload},
        )
        return map_session_exercise(result["addSessionSet"])

    async def update_set(self, set_id: str, payload: dict[str, object]) -> SessionSet:
        result = await self.client.execute(
            UPDATE_SESSION_SET,
            {"id": set_id, "input": payload},
        )
        return map_session_set(result["updateSessionSet"])

    async def remove_set(self, set_id: str) -> bool:
        result = await self.client.execute(REMOVE_SESSION_SET, {"id": set_id})
        return bool(result["removeSessionSet"])

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        result = await self.client.execute(LOG_SET_RESULT, {"setId": set_id, "input": payload})
        return map_session_set(result["logSetResult"])
