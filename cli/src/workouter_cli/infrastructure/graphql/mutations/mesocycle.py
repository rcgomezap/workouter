"""Mesocycle GraphQL mutations."""

from workouter_cli.infrastructure.graphql.queries.mesocycle import MESOCYCLE_FIELDS

CREATE_MESOCYCLE = (
    """
mutation CreateMesocycle($input: CreateMesocycleInput!) {
  createMesocycle(input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_FIELDS
)

UPDATE_MESOCYCLE = (
    """
mutation UpdateMesocycle($id: UUID!, $input: UpdateMesocycleInput!) {
  updateMesocycle(id: $id, input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_FIELDS
)

DELETE_MESOCYCLE = """
mutation DeleteMesocycle($id: UUID!) {
  deleteMesocycle(id: $id)
}
"""
