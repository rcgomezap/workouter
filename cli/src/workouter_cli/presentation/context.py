"""Click dependency-injection context object."""

from __future__ import annotations

from dataclasses import dataclass

from workouter_cli.application.services.exercise_service import ExerciseService
from workouter_cli.infrastructure.config.schema import Config
from workouter_cli.infrastructure.graphql.client import GraphQLClient


@dataclass(slots=True)
class CLIContext:
    """Runtime dependencies shared across commands."""

    config: Config
    client: GraphQLClient
    output_json: bool
    timeout: int
    exercise_service: ExerciseService
