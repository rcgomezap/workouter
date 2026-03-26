import uuid
from datetime import UTC, date, datetime, timedelta

import factory

from app.domain.entities.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.domain.enums import MesocycleStatus, WeekType


class MesocycleFactory(factory.Factory):
    class Meta:
        model = Mesocycle

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Mesocycle {n}")
    description = "Test Mesocycle"
    start_date = factory.LazyFunction(lambda: date.today())
    status = MesocycleStatus.PLANNED
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class MesocycleWeekFactory(factory.Factory):
    class Meta:
        model = MesocycleWeek

    id = factory.LazyFunction(uuid.uuid4)
    mesocycle_id = factory.LazyFunction(uuid.uuid4)
    week_number = factory.Sequence(lambda n: n + 1)
    week_type = WeekType.TRAINING
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=6))


class PlannedSessionFactory(factory.Factory):
    class Meta:
        model = PlannedSession

    id = factory.LazyFunction(uuid.uuid4)
    mesocycle_week_id = factory.LazyFunction(uuid.uuid4)
    routine_id = None
    day_of_week = 0
    date = factory.LazyFunction(lambda: date.today())
    notes = None
