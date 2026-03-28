"""Session GraphQL mutations."""

CREATE_SESSION = """
mutation CreateSession($input: CreateSessionInput!) {
  createSession(input: $input) {
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
}
"""


START_SESSION = """
mutation StartSession($id: UUID!) {
  startSession(id: $id) {
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
}
"""


COMPLETE_SESSION = """
mutation CompleteSession($id: UUID!) {
  completeSession(id: $id) {
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
}
"""


UPDATE_SESSION = """
mutation UpdateSession($id: UUID!, $input: UpdateSessionInput!) {
  updateSession(id: $id, input: $input) {
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
}
"""


LOG_SET_RESULT = """
mutation LogSetResult($setId: UUID!, $input: LogSetResultInput!) {
  logSetResult(setId: $setId, input: $input) {
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
