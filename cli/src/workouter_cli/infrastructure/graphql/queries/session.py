"""Session GraphQL queries."""

LIST_SESSIONS = """
query ListSessions($pagination: PaginationInput, $status: SessionStatus) {
  sessions(pagination: $pagination, status: $status) {
    items {
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
    }
    total
    page
    pageSize
    totalPages
  }
}
"""
