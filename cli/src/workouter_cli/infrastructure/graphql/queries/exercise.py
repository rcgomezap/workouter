"""Exercise GraphQL queries."""

LIST_EXERCISES = """
query ListExercises($pagination: PaginationInput) {
  exercises(pagination: $pagination) {
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
