"""Calendar GraphQL queries."""

CALENDAR_DAY = """
query CalendarDay($date: Date!) {
  calendarDay(date: $date) {
    date
    plannedSession {
      id
      routine {
        id
        name
      }
      dayOfWeek
      date
      notes
    }
    session {
      id
    }
    isCompleted
    isRestDay
  }
}
"""


CALENDAR_RANGE = """
query CalendarRange($startDate: Date!, $endDate: Date!) {
  calendarRange(startDate: $startDate, endDate: $endDate) {
    date
    plannedSession {
      id
      routine {
        id
        name
      }
      dayOfWeek
      date
      notes
    }
    session {
      id
    }
    isCompleted
    isRestDay
  }
}
"""
