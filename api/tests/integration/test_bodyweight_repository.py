from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.bodyweight import BodyweightLog
from app.infrastructure.database.repositories.bodyweight import SQLAlchemyBodyweightRepository


@pytest.mark.asyncio
async def test_bodyweight_repository_list_by_date_range(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyBodyweightRepository(db_session)
    t1 = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    t2 = datetime(2026, 1, 5, 8, 0, tzinfo=UTC)
    t3 = datetime(2026, 1, 10, 8, 0, tzinfo=UTC)

    await repo.add(BodyweightLog(id=uuid4(), weight_kg=Decimal("80.0"), recorded_at=t1))
    await repo.add(BodyweightLog(id=uuid4(), weight_kg=Decimal("81.0"), recorded_at=t2))
    await repo.add(BodyweightLog(id=uuid4(), weight_kg=Decimal("82.0"), recorded_at=t3))

    # Act
    logs = await repo.list_by_date_range(date_from=date(2026, 1, 2), date_to=date(2026, 1, 6))

    # Assert
    assert len(logs) == 1
    assert logs[0].weight_kg == Decimal("81.0")


@pytest.mark.asyncio
async def test_bodyweight_repository_count_by_date_range(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyBodyweightRepository(db_session)
    t1 = datetime(2026, 2, 1, 8, 0, tzinfo=UTC)
    t2 = datetime(2026, 2, 15, 8, 0, tzinfo=UTC)

    await repo.add(BodyweightLog(id=uuid4(), weight_kg=Decimal("70.0"), recorded_at=t1))
    await repo.add(BodyweightLog(id=uuid4(), weight_kg=Decimal("71.0"), recorded_at=t2))

    # Act
    count = await repo.count_by_date_range(date_from=date(2026, 2, 1), date_to=date(2026, 2, 28))

    # Assert
    assert count == 2


@pytest.mark.asyncio
async def test_bodyweight_repository_update(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyBodyweightRepository(db_session)
    log = BodyweightLog(id=uuid4(), weight_kg=Decimal("85.0"), recorded_at=datetime.now(UTC))
    await repo.add(log)

    log.weight_kg = Decimal("84.5")
    log.notes = "New notes"

    # Act
    updated_log = await repo.update(log)
    fetched_log = await repo.get_by_id(log.id)

    # Assert
    assert updated_log.weight_kg == Decimal("84.5")
    assert fetched_log.notes == "New notes"
