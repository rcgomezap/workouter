"""Routine GraphQL queries."""

ROUTINE_FIELDS = """
id
name
description
exercises {
  id
  exercise {
    id
    name
  }
  order
  supersetGroup
  restSeconds
  notes
  sets {
    id
    setNumber
    setType
    targetRepsMin
    targetRepsMax
    targetRir
    targetWeightKg
    weightReductionPct
    restSeconds
  }
}
"""


LIST_ROUTINES = (
    """
query ListRoutines($pagination: PaginationInput) {
  routines(pagination: $pagination) {
    items {
      %s
    }
    total
    page
    pageSize
    totalPages
  }
}
"""
    % ROUTINE_FIELDS
)


GET_ROUTINE = (
    """
query GetRoutine($id: UUID!) {
  routine(id: $id) {
    %s
  }
}
"""
    % ROUTINE_FIELDS
)
