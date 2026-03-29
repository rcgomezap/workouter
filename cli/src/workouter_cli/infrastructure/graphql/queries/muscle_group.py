"""GraphQL queries for muscle group operations."""

LIST_MUSCLE_GROUPS = """
query ListMuscleGroups {
  muscleGroups {
    id
    name
  }
}
"""
