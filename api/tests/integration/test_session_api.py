import pytest
from uuid import uuid4
from datetime import datetime, timedelta, UTC

from app.domain.entities.session import Session
from app.domain.entities.mesocycle import Mesocycle
from app.domain.enums import SessionStatus, MesocycleStatus
from app.infrastructure.database.repositories.session import SQLAlchemySessionRepository
from app.infrastructure.database.repositories.mesocycle import SQLAlchemyMesocycleRepository


@pytest.mark.asyncio
async def test_sessions_filter_by_status(client, auth_headers, db_session):
    repo = SQLAlchemySessionRepository(db_session)

    # Create sessions
    completed_id = uuid4()
    planned_id = uuid4()

    completed = Session(id=completed_id, status=SessionStatus.COMPLETED)
    planned = Session(id=planned_id, status=SessionStatus.PLANNED)

    await repo.add(completed)
    await repo.add(planned)
    await db_session.commit()

    query = """
    query GetSessions($status: SessionStatus) {
        sessions(status: $status) {
            items { id status }
            total
        }
    }
    """

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"status": "COMPLETED"}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data

    items = data["data"]["sessions"]["items"]
    total = data["data"]["sessions"]["total"]

    assert total == 1
    assert len(items) == 1
    assert items[0]["id"] == str(completed_id)
    assert items[0]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_sessions_filter_by_mesocycle(client, auth_headers, db_session):
    repo = SQLAlchemySessionRepository(db_session)
    meso_repo = SQLAlchemyMesocycleRepository(db_session)

    meso1_id = uuid4()
    meso2_id = uuid4()

    # Create Mesocycles first
    today = datetime.now(UTC).date()
    meso1 = Mesocycle(id=meso1_id, name="M1", start_date=today, status=MesocycleStatus.PLANNED)
    meso2 = Mesocycle(id=meso2_id, name="M2", start_date=today, status=MesocycleStatus.PLANNED)
    await meso_repo.add(meso1)
    await meso_repo.add(meso2)
    await db_session.commit()

    s1 = Session(id=uuid4(), mesocycle_id=meso1_id, status=SessionStatus.PLANNED)
    s2 = Session(id=uuid4(), mesocycle_id=meso2_id, status=SessionStatus.PLANNED)

    await repo.add(s1)
    await repo.add(s2)
    await db_session.commit()

    query = """
    query GetSessions($mesocycleId: UUID) {
        sessions(mesocycleId: $mesocycleId) {
            items { id }
            total
        }
    }
    """

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"mesocycleId": str(meso1_id)}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data

    items = data["data"]["sessions"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == str(s1.id)


@pytest.mark.asyncio
async def test_sessions_filter_by_date_range(client, auth_headers, db_session):
    repo = SQLAlchemySessionRepository(db_session)

    today = datetime.now(UTC)
    yesterday = today - timedelta(days=1)

    s1 = Session(id=uuid4(), started_at=today, status=SessionStatus.COMPLETED)
    s2 = Session(id=uuid4(), started_at=yesterday, status=SessionStatus.COMPLETED)

    await repo.add(s1)
    await repo.add(s2)
    await db_session.commit()

    # Filter for today only
    query = """
    query GetSessions($dateFrom: Date, $dateTo: Date) {
        sessions(dateFrom: $dateFrom, dateTo: $dateTo) {
            items { id }
            total
        }
    }
    """

    today_str = today.date().isoformat()

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"dateFrom": today_str, "dateTo": today_str}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data

    items = data["data"]["sessions"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == str(s1.id)
