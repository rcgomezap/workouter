"""Session GraphQL queries."""

SESSION_FIELDS = """
id
plannedSessionId
mesocycleId
routineId
status
startedAt
completedAt
notes
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
    targetReps
    targetRir
    targetWeightKg
    actualReps
    actualRir
    actualWeightKg
    weightReductionPct
    restSeconds
    performedAt
  }
}
"""

LIST_SESSIONS = (
    """
query ListSessions(
  $pagination: PaginationInput
  $status: SessionStatus
  $mesocycleId: UUID
  $dateFrom: Date
  $dateTo: Date
) {
  sessions(
    pagination: $pagination
    status: $status
    mesocycleId: $mesocycleId
    dateFrom: $dateFrom
    dateTo: $dateTo
  ) {
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
    % SESSION_FIELDS
)

GET_SESSION = (
    """
query GetSession($id: UUID!) {
  session(id: $id) {
    %s
  }
}
"""
    % SESSION_FIELDS
)
