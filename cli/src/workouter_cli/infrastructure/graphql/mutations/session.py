"""Session GraphQL mutations."""

from workouter_cli.infrastructure.graphql.queries.session import SESSION_FIELDS

SESSION_EXERCISE_FIELDS = """
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
"""

SESSION_SET_FIELDS = """
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
"""

CREATE_SESSION = (
    """
mutation CreateSession($input: CreateSessionInput!) {
  createSession(input: $input) {
    %s
  }
}
"""
    % SESSION_FIELDS
)


START_SESSION = (
    """
mutation StartSession($id: UUID!) {
  startSession(id: $id) {
    %s
  }
}
"""
    % SESSION_FIELDS
)


COMPLETE_SESSION = (
    """
mutation CompleteSession($id: UUID!) {
  completeSession(id: $id) {
    %s
  }
}
"""
    % SESSION_FIELDS
)


UPDATE_SESSION = (
    """
mutation UpdateSession($id: UUID!, $input: UpdateSessionInput!) {
  updateSession(id: $id, input: $input) {
    %s
  }
}
"""
    % SESSION_FIELDS
)


DELETE_SESSION = """
mutation DeleteSession($id: UUID!) {
  deleteSession(id: $id)
}
"""


ADD_SESSION_EXERCISE = (
    """
mutation AddSessionExercise($sessionId: UUID!, $input: AddSessionExerciseInput!) {
  addSessionExercise(sessionId: $sessionId, input: $input) {
    %s
  }
}
"""
    % SESSION_FIELDS
)


UPDATE_SESSION_EXERCISE = (
    """
mutation UpdateSessionExercise($id: UUID!, $input: UpdateSessionExerciseInput!) {
  updateSessionExercise(id: $id, input: $input) {
    %s
  }
}
"""
    % SESSION_EXERCISE_FIELDS
)


REMOVE_SESSION_EXERCISE = """
mutation RemoveSessionExercise($id: UUID!) {
  removeSessionExercise(id: $id)
}
"""


ADD_SESSION_SET = (
    """
mutation AddSessionSet($sessionExerciseId: UUID!, $input: AddSessionSetInput!) {
  addSessionSet(sessionExerciseId: $sessionExerciseId, input: $input) {
    %s
  }
}
"""
    % SESSION_EXERCISE_FIELDS
)


UPDATE_SESSION_SET = (
    """
mutation UpdateSessionSet($id: UUID!, $input: UpdateSessionSetInput!) {
  updateSessionSet(id: $id, input: $input) {
    %s
  }
}
"""
    % SESSION_SET_FIELDS
)


REMOVE_SESSION_SET = """
mutation RemoveSessionSet($id: UUID!) {
  removeSessionSet(id: $id)
}
"""


LOG_SET_RESULT = (
    """
mutation LogSetResult($setId: UUID!, $input: LogSetResultInput!) {
  logSetResult(setId: $setId, input: $input) {
    %s
  }
}
"""
    % SESSION_SET_FIELDS
)
