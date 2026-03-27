from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.domain.exceptions import APIError, AuthError, NetworkError, ValidationError
from workouter_cli.infrastructure.graphql.client import GraphQLClient, map_graphql_error


def test_graphql_client_builds_transport() -> None:
    client = GraphQLClient(url="http://localhost:8000/graphql", api_key="k", timeout=45)

    assert str(client.transport.url) == "http://localhost:8000/graphql"
    assert client.transport.kwargs["headers"] == {"Authorization": "Bearer k"}
    assert client.transport.kwargs["timeout"] == 45


@pytest.mark.asyncio
async def test_graphql_client_execute_calls_session_with_variables() -> None:
    client = GraphQLClient(url="http://localhost:8000/graphql", api_key="k", timeout=30)

    session = AsyncMock()
    session.execute = AsyncMock(return_value={"ok": True})

    class DummyContext:
        async def __aenter__(self) -> AsyncMock:
            return session

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
            return None

    client.client = DummyContext()  # type: ignore[assignment]

    result = await client.execute("query Ping { ping }", {"x": 1})

    assert result == {"ok": True}
    session.execute.assert_awaited_once()
    assert session.execute.await_args.kwargs["variable_values"] == {"x": 1}


def test_map_graphql_error_validation() -> None:
    err = map_graphql_error({"message": "invalid", "extensions": {"code": "VALIDATION_ERROR"}})
    assert isinstance(err, ValidationError)


def test_map_graphql_error_api() -> None:
    err = map_graphql_error({"message": "missing", "extensions": {"code": "NOT_FOUND"}})
    assert isinstance(err, APIError)


def test_map_graphql_error_auth() -> None:
    err = map_graphql_error({"message": "no auth", "extensions": {"code": "AUTH_ERROR"}})
    assert isinstance(err, AuthError)


def test_map_graphql_error_fallback() -> None:
    err = map_graphql_error({"message": "boom", "extensions": {"code": "SOMETHING_ELSE"}})
    assert isinstance(err, NetworkError)
