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
