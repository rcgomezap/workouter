"""Routine GraphQL mutations."""

from workouter_cli.infrastructure.graphql.queries.routine import ROUTINE_FIELDS

ROUTINE_EXERCISE_FIELDS = """
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
"""

ROUTINE_SET_FIELDS = """
id
setNumber
setType
targetRepsMin
targetRepsMax
targetRir
targetWeightKg
weightReductionPct
restSeconds
"""

ADD_ROUTINE_EXERCISE = (
    """
mutation AddRoutineExercise($routineId: UUID!, $input: AddRoutineExerciseInput!) {
  addRoutineExercise(routineId: $routineId, input: $input) {
    %s
  }
}
"""
    % ROUTINE_FIELDS
)


UPDATE_ROUTINE_EXERCISE = (
    """
mutation UpdateRoutineExercise($id: UUID!, $input: UpdateRoutineExerciseInput!) {
  updateRoutineExercise(id: $id, input: $input) {
    %s
  }
}
"""
    % ROUTINE_EXERCISE_FIELDS
)


REMOVE_ROUTINE_EXERCISE = """
mutation RemoveRoutineExercise($id: UUID!) {
  removeRoutineExercise(id: $id)
}
"""


ADD_ROUTINE_SET = (
    """
mutation AddRoutineSet($routineExerciseId: UUID!, $input: AddRoutineSetInput!) {
  addRoutineSet(routineExerciseId: $routineExerciseId, input: $input) {
    %s
  }
}
"""
    % ROUTINE_EXERCISE_FIELDS
)


UPDATE_ROUTINE_SET = (
    """
mutation UpdateRoutineSet($id: UUID!, $input: UpdateRoutineSetInput!) {
  updateRoutineSet(id: $id, input: $input) {
    %s
  }
}
"""
    % ROUTINE_SET_FIELDS
)


REMOVE_ROUTINE_SET = """
mutation RemoveRoutineSet($id: UUID!) {
  removeRoutineSet(id: $id)
}
"""
