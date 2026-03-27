"""GraphQL infrastructure package."""

from workouter_cli.infrastructure.graphql.client import GraphQLClient, map_graphql_error

__all__ = ["GraphQLClient", "map_graphql_error"]
