"""GraphQL-backed session repository implementation."""

from __future__ import annotations

from workouter_cli.domain.entities.session import Session, SessionSet
from workouter_cli.domain.repositories.session import SessionRepository
from workouter_cli.infrastructure.graphql.client import GraphQLClient
from workouter_cli.infrastructure.graphql.mappers.response_mapper import (
    map_session,
    map_session_set,
)
from workouter_cli.infrastructure.graphql.mutations.session import (
    COMPLETE_SESSION,
    CREATE_SESSION,
    LOG_SET_RESULT,
    START_SESSION,
)


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

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        result = await self.client.execute(LOG_SET_RESULT, {"setId": set_id, "input": payload})
        return map_session_set(result["logSetResult"])
