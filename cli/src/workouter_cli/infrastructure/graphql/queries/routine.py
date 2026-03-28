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
