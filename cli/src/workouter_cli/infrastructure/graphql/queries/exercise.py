"""Exercise GraphQL queries."""

LIST_EXERCISES = """
query ListExercises($pagination: PaginationInput, $muscleGroupId: UUID) {
  exercises(pagination: $pagination, muscleGroupId: $muscleGroupId) {
    items {
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
    total
    page
    pageSize
    totalPages
  }
}
"""


GET_EXERCISE = """
query GetExercise($id: UUID!) {
  exercise(id: $id) {
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
