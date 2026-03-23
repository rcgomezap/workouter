import factory
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.enums import SetType
import uuid
from datetime import datetime, UTC

class RoutineFactory(factory.Factory):
    class Meta:
        model = Routine

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Routine {n}")
    description = "Test Routine"
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))

class RoutineExerciseFactory(factory.Factory):
    class Meta:
        model = RoutineExercise

    id = factory.LazyFunction(uuid.uuid4)
    routine_id = factory.LazyFunction(uuid.uuid4)
    exercise_id = factory.LazyFunction(uuid.uuid4)
    order = factory.Sequence(lambda n: n)
    superset_group = None
    rest_seconds = 60
    notes = None

class RoutineSetFactory(factory.Factory):
    class Meta:
        model = RoutineSet

    id = factory.LazyFunction(uuid.uuid4)
    routine_exercise_id = factory.LazyFunction(uuid.uuid4)
    set_number = factory.Sequence(lambda n: n + 1)
    set_type = SetType.STANDARD
    target_reps_min = 8
    target_reps_max = 12
    target_rir = 2
    target_weight_kg = 50.0
    weight_reduction_pct = None
    rest_seconds = 60
