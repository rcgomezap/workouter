import factory
from app.domain.entities.bodyweight import BodyweightLog
import uuid
from datetime import datetime, UTC

class BodyweightLogFactory(factory.Factory):
    class Meta:
        model = BodyweightLog

    id = factory.LazyFunction(uuid.uuid4)
    weight_kg = factory.Sequence(lambda n: 70.0 + n * 0.1)
    recorded_at = factory.LazyFunction(lambda: datetime.now(UTC))
    notes = "Test Bodyweight Log"
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
