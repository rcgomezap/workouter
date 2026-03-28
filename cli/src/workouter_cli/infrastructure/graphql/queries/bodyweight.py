"""Bodyweight GraphQL queries."""

LIST_BODYWEIGHT_LOGS = """
query ListBodyweightLogs($pagination: PaginationInput, $dateFrom: DateTime, $dateTo: DateTime) {
  bodyweightLogs(pagination: $pagination, dateFrom: $dateFrom, dateTo: $dateTo) {
    items {
      id
      weightKg
      recordedAt
      notes
      createdAt
    }
    total
    page
    pageSize
    totalPages
  }
}
"""
