from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.bodyweight import BodyweightLog
from app.infrastructure.database.repositories.bodyweight import SQLAlchemyBodyweightRepository


@pytest.fixture
async def bodyweight_repo(db_session):
    return SQLAlchemyBodyweightRepository(db_session)


@pytest.mark.asyncio
async def test_bodyweight_logs_filter_by_date_from(
    client, auth_headers, bodyweight_repo, db_session
):
    # Setup: Create bodyweight logs on different dates
    today = datetime.now(UTC)
    last_week = today - timedelta(days=7)
    next_week = today + timedelta(days=7)

    log1 = BodyweightLog(
        id=uuid4(), weight_kg=Decimal("80.0"), recorded_at=last_week, notes="Old log"
    )
    log2 = BodyweightLog(
        id=uuid4(), weight_kg=Decimal("81.0"), recorded_at=today, notes="Today log"
    )
    log3 = BodyweightLog(
        id=uuid4(), weight_kg=Decimal("82.0"), recorded_at=next_week, notes="Future log"
    )

    await bodyweight_repo.add(log1)
    await bodyweight_repo.add(log2)
    await bodyweight_repo.add(log3)
    await db_session.commit()

    # Query with date_from filter (should include today and future)
    # Using today as dateFrom
    query = """
    query GetBodyweightLogs($dateFrom: DateTime) {
        bodyweightLogs(dateFrom: $dateFrom) {
            items {
                id
                weightKg
                recordedAt
            }
            total
        }
    }
    """

    # GraphQL DateTime is ISO format string
    date_from_str = today.isoformat()

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"dateFrom": date_from_str}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data

    items = data["data"]["bodyweightLogs"]["items"]
    total = data["data"]["bodyweightLogs"]["total"]

    # Should find log2 and log3 (recorded_at >= today)
    # Note: recorded_at is datetime, date_from is passed as date in service
    # If recorded_at is today 10:00 and date_from is today (00:00), it should be included.

    # Wait, the logic is: recorded_at >= date_from (converted to date)
    # Repository implementation: func.date(recorded_at) >= date_from
    # So if recorded_at is today, func.date(recorded_at) is today. today >= today is True.

    assert total == 2
    ids = [item["id"] for item in items]
    assert str(log2.id) in ids
    assert str(log3.id) in ids
    assert str(log1.id) not in ids


@pytest.mark.asyncio
async def test_bodyweight_logs_filter_by_date_to(client, auth_headers, bodyweight_repo, db_session):
    # Setup
    today = datetime.now(UTC)
    last_week = today - timedelta(days=7)
    next_week = today + timedelta(days=7)

    log1 = BodyweightLog(id=uuid4(), weight_kg=Decimal("80.0"), recorded_at=last_week)
    log2 = BodyweightLog(id=uuid4(), weight_kg=Decimal("81.0"), recorded_at=today)
    log3 = BodyweightLog(id=uuid4(), weight_kg=Decimal("82.0"), recorded_at=next_week)

    await bodyweight_repo.add(log1)
    await bodyweight_repo.add(log2)
    await bodyweight_repo.add(log3)
    await db_session.commit()

    # Query with date_to filter (should include old and today)
    query = """
    query GetBodyweightLogs($dateTo: DateTime) {
        bodyweightLogs(dateTo: $dateTo) {
            items { id }
            total
        }
    }
    """

    date_to_str = today.isoformat()

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"dateTo": date_to_str}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    items = data["data"]["bodyweightLogs"]["items"]
    total = data["data"]["bodyweightLogs"]["total"]

    assert total == 2
    ids = [item["id"] for item in items]
    assert str(log1.id) in ids
    assert str(log2.id) in ids
    assert str(log3.id) not in ids


@pytest.mark.asyncio
async def test_bodyweight_logs_filter_by_date_range(
    client, auth_headers, bodyweight_repo, db_session
):
    # Setup
    today = datetime.now(UTC)
    last_week = today - timedelta(days=7)
    next_week = today + timedelta(days=7)

    log1 = BodyweightLog(id=uuid4(), weight_kg=Decimal("80.0"), recorded_at=last_week)
    log2 = BodyweightLog(id=uuid4(), weight_kg=Decimal("81.0"), recorded_at=today)
    log3 = BodyweightLog(id=uuid4(), weight_kg=Decimal("82.0"), recorded_at=next_week)

    await bodyweight_repo.add(log1)
    await bodyweight_repo.add(log2)
    await bodyweight_repo.add(log3)
    await db_session.commit()

    # Filter for today only (dateFrom = today, dateTo = today)
    query = """
    query GetBodyweightLogs($dateFrom: DateTime, $dateTo: DateTime) {
        bodyweightLogs(dateFrom: $dateFrom, dateTo: $dateTo) {
            items { id }
            total
        }
    }
    """

    today_str = today.isoformat()

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"dateFrom": today_str, "dateTo": today_str}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    items = data["data"]["bodyweightLogs"]["items"]
    total = data["data"]["bodyweightLogs"]["total"]

    assert total == 1
    assert items[0]["id"] == str(log2.id)


@pytest.mark.asyncio
async def test_bodyweight_logs_pagination_with_filters(
    client, auth_headers, bodyweight_repo, db_session
):
    # Create multiple logs for today
    today = datetime.now(UTC)
    logs = []
    for i in range(5):
        log = BodyweightLog(
            id=uuid4(), weight_kg=Decimal(f"80.{i}"), recorded_at=today + timedelta(hours=i)
        )
        logs.append(log)
        await bodyweight_repo.add(log)

    # Add one for yesterday (should be filtered out)
    yesterday = today - timedelta(days=1)
    old_log = BodyweightLog(id=uuid4(), weight_kg=Decimal("79.0"), recorded_at=yesterday)
    await bodyweight_repo.add(old_log)

    await db_session.commit()

    # Query: Filter by today, Page 1, size 2
    query = """
    query GetBodyweightLogs($dateFrom: DateTime, $page: Int, $pageSize: Int) {
        bodyweightLogs(dateFrom: $dateFrom, pagination: {page: $page, pageSize: $pageSize}) {
            items { id }
            total
            page
            pageSize
            totalPages
        }
    }
    """

    today_str = today.isoformat()

    response = await client.post(
        "/graphql",
        json={"query": query, "variables": {"dateFrom": today_str, "page": 1, "pageSize": 2}},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    result = data["data"]["bodyweightLogs"]

    assert result["total"] == 5
    assert len(result["items"]) == 2
    assert result["totalPages"] == 3
