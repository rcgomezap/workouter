"""Mesocycle GraphQL mutations."""

from workouter_cli.infrastructure.graphql.queries.mesocycle import MESOCYCLE_FIELDS

MESOCYCLE_WEEK_FIELDS = """
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
"""

PLANNED_SESSION_FIELDS = """
id
routine {
  id
  name
}
dayOfWeek
date
notes
"""

CREATE_MESOCYCLE = (
    """
mutation CreateMesocycle($input: CreateMesocycleInput!) {
  createMesocycle(input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_FIELDS
)

UPDATE_MESOCYCLE = (
    """
mutation UpdateMesocycle($id: UUID!, $input: UpdateMesocycleInput!) {
  updateMesocycle(id: $id, input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_FIELDS
)

DELETE_MESOCYCLE = """
mutation DeleteMesocycle($id: UUID!) {
  deleteMesocycle(id: $id)
}
"""


ADD_MESOCYCLE_WEEK = (
    """
mutation AddMesocycleWeek($mesocycleId: UUID!, $input: AddMesocycleWeekInput!) {
  addMesocycleWeek(mesocycleId: $mesocycleId, input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_WEEK_FIELDS
)


UPDATE_MESOCYCLE_WEEK = (
    """
mutation UpdateMesocycleWeek($id: UUID!, $input: UpdateMesocycleWeekInput!) {
  updateMesocycleWeek(id: $id, input: $input) {
    %s
  }
}
"""
    % MESOCYCLE_WEEK_FIELDS
)


REMOVE_MESOCYCLE_WEEK = """
mutation RemoveMesocycleWeek($id: UUID!) {
  removeMesocycleWeek(id: $id)
}
"""


ADD_PLANNED_SESSION = (
    """
mutation AddPlannedSession($mesocycleWeekId: UUID!, $input: AddPlannedSessionInput!) {
  addPlannedSession(mesocycleWeekId: $mesocycleWeekId, input: $input) {
    %s
  }
}
"""
    % PLANNED_SESSION_FIELDS
)


UPDATE_PLANNED_SESSION = (
    """
mutation UpdatePlannedSession($id: UUID!, $input: UpdatePlannedSessionInput!) {
  updatePlannedSession(id: $id, input: $input) {
    %s
  }
}
"""
    % PLANNED_SESSION_FIELDS
)


REMOVE_PLANNED_SESSION = """
mutation RemovePlannedSession($id: UUID!) {
  removePlannedSession(id: $id)
}
"""
