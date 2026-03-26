import uuid
from datetime import UTC, datetime

import factory

from app.domain.entities.exercise import Exercise
from app.domain.entities.muscle_group import MuscleGroup


class MuscleGroupFactory(factory.Factory):
    class Meta:
        model = MuscleGroup

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Muscle Group {n}")

class ExerciseFactory(factory.Factory):
    class Meta:
        model = Exercise

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Exercise {n}")
    description = "Test Description"
    equipment = "Dumbbell"
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
