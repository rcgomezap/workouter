"""Bodyweight GraphQL mutations."""

LOG_BODYWEIGHT = """
mutation LogBodyweight($input: LogBodyweightInput!) {
  logBodyweight(input: $input) {
    id
    weightKg
    recordedAt
    notes
    createdAt
  }
}
"""


UPDATE_BODYWEIGHT_LOG = """
mutation UpdateBodyweightLog($id: UUID!, $input: UpdateBodyweightInput!) {
  updateBodyweightLog(id: $id, input: $input) {
    id
    weightKg
    recordedAt
    notes
    createdAt
  }
}
"""


DELETE_BODYWEIGHT_LOG = """
mutation DeleteBodyweightLog($id: UUID!) {
  deleteBodyweightLog(id: $id)
}
"""
