import pytest
from uuid import uuid4
from datetime import datetime, date, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.session import Session
from app.domain.enums import SessionStatus
from app.infrastructure.database.repositories.session import SQLAlchemySessionRepository


@pytest.mark.asyncio
async def test_session_repository_filter_by_status(db_session: AsyncSession):
    repo = SQLAlchemySessionRepository(db_session)

    # Create sessions with different statuses
    completed = Session(
        id=uuid4(),
        status=SessionStatus.COMPLETED,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    planned = Session(id=uuid4(), status=SessionStatus.PLANNED)

    await repo.add(completed)
    await repo.add(planned)
    await db_session.commit()

    # Filter by completed
    results = await repo.list_by_filters(status=SessionStatus.COMPLETED)
    count = await repo.count_by_filters(status=SessionStatus.COMPLETED)

    # Assert
    assert len(results) == 1
    assert results[0].id == completed.id
    assert results[0].status == SessionStatus.COMPLETED
    assert count == 1

    # Filter by planned
    results = await repo.list_by_filters(status=SessionStatus.PLANNED)
    count = await repo.count_by_filters(status=SessionStatus.PLANNED)

    # Assert
    assert len(results) == 1
    assert results[0].id == planned.id
    assert count == 1


@pytest.mark.asyncio
async def test_session_repository_filter_by_mesocycle(db_session: AsyncSession):
    repo = SQLAlchemySessionRepository(db_session)

    meso1_id = uuid4()
    meso2_id = uuid4()

    # Create sessions for different mesocycles
    s1 = Session(id=uuid4(), mesocycle_id=meso1_id, status=SessionStatus.PLANNED)
    s2 = Session(id=uuid4(), mesocycle_id=meso2_id, status=SessionStatus.PLANNED)

    await repo.add(s1)
    await repo.add(s2)
    await db_session.commit()

    # Filter by meso1
    results = await repo.list_by_filters(mesocycle_id=meso1_id)
    count = await repo.count_by_filters(mesocycle_id=meso1_id)

    # Assert
    assert len(results) == 1
    assert results[0].id == s1.id
    assert count == 1


@pytest.mark.asyncio
async def test_session_repository_filter_by_date_range(db_session: AsyncSession):
    repo = SQLAlchemySessionRepository(db_session)

    today = datetime.now(UTC)
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    # Create sessions with different dates
    s_today = Session(id=uuid4(), started_at=today, status=SessionStatus.COMPLETED)
    s_yesterday = Session(id=uuid4(), started_at=yesterday, status=SessionStatus.COMPLETED)
    s_last_week = Session(id=uuid4(), started_at=last_week, status=SessionStatus.COMPLETED)

    await repo.add(s_today)
    await repo.add(s_yesterday)
    await repo.add(s_last_week)
    await db_session.commit()

    # Filter from 2 days ago to tomorrow (should include today and yesterday)
    date_from = (today - timedelta(days=2)).date()
    date_to = (today + timedelta(days=1)).date()

    results = await repo.list_by_filters(date_from=date_from, date_to=date_to)
    count = await repo.count_by_filters(date_from=date_from, date_to=date_to)

    # Assert
    assert len(results) == 2
    ids = {s.id for s in results}
    assert s_today.id in ids
    assert s_yesterday.id in ids
    assert s_last_week.id not in ids
    assert count == 2


@pytest.mark.asyncio
async def test_session_repository_combined_filters(db_session: AsyncSession):
    repo = SQLAlchemySessionRepository(db_session)

    meso_id = uuid4()
    today = datetime.now(UTC)

    # Target session
    s1 = Session(id=uuid4(), mesocycle_id=meso_id, status=SessionStatus.COMPLETED, started_at=today)

    # Wrong status
    s2 = Session(
        id=uuid4(),
        mesocycle_id=meso_id,
        status=SessionStatus.PLANNED,  # Wrong status
        started_at=today,
    )

    # Wrong mesocycle
    s3 = Session(
        id=uuid4(),
        mesocycle_id=uuid4(),  # Wrong meso
        status=SessionStatus.COMPLETED,
        started_at=today,
    )

    # Wrong date (too old)
    s4 = Session(
        id=uuid4(),
        mesocycle_id=meso_id,
        status=SessionStatus.COMPLETED,
        started_at=today - timedelta(days=10),
    )

    await repo.add(s1)
    await repo.add(s2)
    await repo.add(s3)
    await repo.add(s4)
    await db_session.commit()

    # Apply all filters
    results = await repo.list_by_filters(
        status=SessionStatus.COMPLETED,
        mesocycle_id=meso_id,
        date_from=(today - timedelta(days=1)).date(),
    )

    # Assert
    assert len(results) == 1
    assert results[0].id == s1.id
