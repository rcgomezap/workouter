"""GraphQL client wrapper and error mapping utilities."""

from __future__ import annotations

from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport

from workouter_cli.domain.exceptions import (
    APIError,
    AuthError,
    CLIError,
    NetworkError,
    ValidationError,
)


class GraphQLClient:
    """Thin wrapper around gql client with configured transport."""

    def __init__(self, url: str, api_key: str, timeout: int) -> None:
        self.transport = HTTPXAsyncTransport(
            url=url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)

    async def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query/mutation asynchronously."""

        async with self.client as session:
            result = await session.execute(gql(query), variable_values=variables)
            return dict(result)


def map_graphql_error(error: dict[str, Any]) -> CLIError:
    """Map GraphQL error payload to domain-specific CLI exceptions."""

    message = str(error.get("message", "Unexpected GraphQL error"))
    extensions = error.get("extensions")
    if isinstance(extensions, dict):
        code = str(extensions.get("code", "INTERNAL_ERROR"))
    else:
        code = "INTERNAL_ERROR"

    if code == "VALIDATION_ERROR":
        return ValidationError(message=message, code=code)
    if code in {"NOT_FOUND", "CONFLICT", "API_ERROR"}:
        return APIError(message=message, code=code)
    if code in {"AUTH_ERROR", "UNAUTHORIZED"}:
        return AuthError(message=message, code=code)
    return NetworkError(message=message, code=code)
