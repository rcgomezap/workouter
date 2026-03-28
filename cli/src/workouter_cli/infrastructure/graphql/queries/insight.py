"""Insights GraphQL queries."""

MESOCYCLE_VOLUME_INSIGHT = """
query MesocycleVolumeInsight($mesocycleId: UUID!, $muscleGroupId: UUID) {
  mesocycleVolumeInsight(mesocycleId: $mesocycleId, muscleGroupId: $muscleGroupId) {
    mesocycleId
    weeklyVolumes {
      weekNumber
      muscleGroupId
      muscleGroupName
      setCount
    }
    totalSets
    muscleGroupBreakdown {
      muscleGroupId
      muscleGroupName
      totalSets
    }
  }
}
"""

MESOCYCLE_INTENSITY_INSIGHT = """
query MesocycleIntensityInsight($mesocycleId: UUID!) {
  mesocycleIntensityInsight(mesocycleId: $mesocycleId) {
    mesocycleId
    weeklyIntensities {
      weekNumber
      avgRir
    }
    overallAvgRir
  }
}
"""

PROGRESSIVE_OVERLOAD_INSIGHT = """
query ProgressiveOverloadInsight($mesocycleId: UUID!, $exerciseId: UUID!) {
  progressiveOverloadInsight(mesocycleId: $mesocycleId, exerciseId: $exerciseId) {
    exerciseId
    mesocycleId
    weeklyProgress {
      weekNumber
      maxWeight
      avgReps
      avgRir
    }
    estimatedOneRepMaxProgression
  }
}
"""

EXERCISE_HISTORY = """
query ExerciseHistory($exerciseId: UUID!, $routineId: UUID, $pagination: PaginationInput) {
  exerciseHistory(exerciseId: $exerciseId, routineId: $routineId, pagination: $pagination) {
    items {
      id
      plannedSessionId
      mesocycleId
      routineId
      status
      startedAt
      completedAt
      notes
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
          targetReps
          targetRir
          targetWeightKg
          actualReps
          actualRir
          actualWeightKg
          weightReductionPct
          restSeconds
          performedAt
        }
      }
    }
    total
    page
    pageSize
    totalPages
  }
}
"""
