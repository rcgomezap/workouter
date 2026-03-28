"""Mesocycle GraphQL queries."""

MESOCYCLE_FIELDS = """
id
name
description
startDate
endDate
status
weeks {
  id
  weekNumber
  weekType
  startDate
  endDate
  plannedSessions {
    id
    routine {
      id
      name
    }
    dayOfWeek
    date
    notes
  }
}
"""

LIST_MESOCYCLES = (
    """
query ListMesocycles($pagination: PaginationInput, $status: MesocycleStatus) {
  mesocycles(pagination: $pagination, status: $status) {
    items {
      %s
    }
    total
    page
    pageSize
    totalPages
  }
}
"""
    % MESOCYCLE_FIELDS
)

GET_MESOCYCLE = (
    """
query GetMesocycle($id: UUID!) {
  mesocycle(id: $id) {
    %s
  }
}
"""
    % MESOCYCLE_FIELDS
)
