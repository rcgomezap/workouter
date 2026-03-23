import factory
from app.domain.entities.session import Session, SessionExercise, SessionSet
from app.domain.enums import SessionStatus, SetType
import uuid
from datetime import datetime, UTC

class SessionFactory(factory.Factory):
    class Meta:
        model = Session

    id = factory.LazyFunction(uuid.uuid4)
    planned_session_id = None
    mesocycle_id = None
    routine_id = None
    status = SessionStatus.PLANNED
    started_at = None
    completed_at = None
    notes = None
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))

class SessionExerciseFactory(factory.Factory):
    class Meta:
        model = SessionExercise

    id = factory.LazyFunction(uuid.uuid4)
    session_id = factory.LazyFunction(uuid.uuid4)
    exercise_id = factory.LazyFunction(uuid.uuid4)
    order = factory.Sequence(lambda n: n)
    superset_group = None
    rest_seconds = 60
    notes = None

class SessionSetFactory(factory.Factory):
    class Meta:
        model = SessionSet

    id = factory.LazyFunction(uuid.uuid4)
    session_exercise_id = factory.LazyFunction(uuid.uuid4)
    set_number = factory.Sequence(lambda n: n + 1)
    set_type = SetType.STANDARD
    target_reps = 10
    target_rir = 2
    target_weight_kg = 50.0
    actual_reps = None
    actual_rir = None
    actual_weight_kg = None
    weight_reduction_pct = None
    rest_seconds = 60
    performed_at = None
