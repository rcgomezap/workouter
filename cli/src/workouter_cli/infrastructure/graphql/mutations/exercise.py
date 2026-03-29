"""Exercise GraphQL mutations."""

CREATE_EXERCISE = """
mutation CreateExercise($input: CreateExerciseInput!) {
  createExercise(input: $input) {
    id
    name
    description
    equipment
    muscleGroups {
      muscleGroup {
        id
        name
      }
      role
    }
  }
}
"""


UPDATE_EXERCISE = """
mutation UpdateExercise($id: UUID!, $input: UpdateExerciseInput!) {
  updateExercise(id: $id, input: $input) {
    id
    name
    description
    equipment
    muscleGroups {
      muscleGroup {
        id
        name
      }
      role
    }
  }
}
"""


DELETE_EXERCISE = """
mutation DeleteExercise($id: UUID!) {
  deleteExercise(id: $id)
}
"""


ASSIGN_MUSCLE_GROUPS = """
mutation AssignMuscleGroups($exerciseId: UUID!, $muscleGroupIds: [MuscleGroupAssignmentInput!]!) {
  assignMuscleGroups(exerciseId: $exerciseId, muscleGroupIds: $muscleGroupIds) {
    id
    name
    description
    equipment
    muscleGroups {
      muscleGroup {
        id
        name
      }
      role
    }
  }
}
"""
