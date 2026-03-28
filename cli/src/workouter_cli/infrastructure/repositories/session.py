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
    UPDATE_SESSION,
)
from workouter_cli.infrastructure.graphql.queries.session import LIST_SESSIONS


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
    ) -> tuple[list[Session], dict[str, int]]:
        variables = {
            "pagination": {"page": page, "pageSize": page_size},
            "status": status,
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

    async def log_set(
        self, set_id: str, payload: dict[str, int | float | str | None]
    ) -> SessionSet:
        result = await self.client.execute(LOG_SET_RESULT, {"setId": set_id, "input": payload})
        return map_session_set(result["logSetResult"])
