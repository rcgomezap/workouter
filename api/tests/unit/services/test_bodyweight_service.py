from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dto.bodyweight import LogBodyweightInput, UpdateBodyweightInput
from app.application.dto.pagination import PaginationInput
from app.application.services.bodyweight_service import BodyweightService
from app.domain.entities.bodyweight import BodyweightLog
from app.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return BodyweightService(mock_uow)


@pytest.mark.asyncio
async def test_get_bodyweight_log_success(service, mock_uow):
    # Arrange
    log_id = uuid4()
    log = BodyweightLog(
        id=log_id, weight_kg=Decimal("80.5"), recorded_at=datetime.now(UTC), notes="Morning weight"
    )
    mock_uow.bodyweight_repository.get_by_id = AsyncMock(return_value=log)

    # Act
    result = await service.get_bodyweight_log(log_id)

    # Assert
    assert result.id == log_id
    assert result.weight_kg == Decimal("80.5")
    mock_uow.bodyweight_repository.get_by_id.assert_called_once_with(log_id)


@pytest.mark.asyncio
async def test_get_bodyweight_log_not_found(service, mock_uow):
    # Arrange
    log_id = uuid4()
    mock_uow.bodyweight_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_bodyweight_log(log_id)


@pytest.mark.asyncio
async def test_list_bodyweight_logs(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    logs = [
        BodyweightLog(id=uuid4(), weight_kg=Decimal("80.0"), recorded_at=datetime.now(UTC)),
        BodyweightLog(id=uuid4(), weight_kg=Decimal("81.0"), recorded_at=datetime.now(UTC)),
    ]
    # Update mocks to use list_by_date_range and count_by_date_range
    mock_uow.bodyweight_repository.list_by_date_range = AsyncMock(return_value=logs)
    mock_uow.bodyweight_repository.count_by_date_range = AsyncMock(return_value=2)

    # Act
    result = await service.list_bodyweight_logs(pagination)

    # Assert
    assert len(result.items) == 2
    assert result.total == 2
    assert result.total_pages == 1
    mock_uow.bodyweight_repository.list_by_date_range.assert_called_once_with(
        date_from=None, date_to=None, offset=0, limit=10
    )
    mock_uow.bodyweight_repository.count_by_date_range.assert_called_once_with(
        date_from=None, date_to=None
    )


@pytest.mark.asyncio
async def test_list_bodyweight_logs_with_date_filters(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    logs = []
    date_from = date(2023, 1, 1)
    date_to = date(2023, 1, 31)

    mock_uow.bodyweight_repository.list_by_date_range = AsyncMock(return_value=logs)
    mock_uow.bodyweight_repository.count_by_date_range = AsyncMock(return_value=0)

    # Act
    result = await service.list_bodyweight_logs(
        pagination=pagination,
        date_from=date_from,
        date_to=date_to,
    )

    # Assert
    assert len(result.items) == 0
    assert result.total == 0
    mock_uow.bodyweight_repository.list_by_date_range.assert_called_once_with(
        date_from=date_from, date_to=date_to, offset=0, limit=10
    )
    mock_uow.bodyweight_repository.count_by_date_range.assert_called_once_with(
        date_from=date_from, date_to=date_to
    )


@pytest.mark.asyncio
async def test_list_bodyweight_logs_with_partial_date_filters(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    logs = []
    date_from = date(2023, 1, 1)

    mock_uow.bodyweight_repository.list_by_date_range = AsyncMock(return_value=logs)
    mock_uow.bodyweight_repository.count_by_date_range = AsyncMock(return_value=0)

    # Act
    await service.list_bodyweight_logs(
        pagination=pagination,
        date_from=date_from,
    )

    # Assert
    mock_uow.bodyweight_repository.list_by_date_range.assert_called_once_with(
        date_from=date_from, date_to=None, offset=0, limit=10
    )
    mock_uow.bodyweight_repository.count_by_date_range.assert_called_once_with(
        date_from=date_from, date_to=None
    )


@pytest.mark.asyncio
async def test_log_bodyweight(service, mock_uow):
    # Arrange
    input_data = LogBodyweightInput(
        weight_kg=Decimal("75.2"), recorded_at=datetime.now(UTC), notes="After workout"
    )
    mock_uow.bodyweight_repository.add = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.log_bodyweight(input_data)

    # Assert
    assert result.weight_kg == Decimal("75.2")
    assert result.notes == "After workout"
    mock_uow.bodyweight_repository.add.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_bodyweight_log_success(service, mock_uow):
    # Arrange
    log_id = uuid4()
    existing_log = BodyweightLog(
        id=log_id, weight_kg=Decimal("80.0"), recorded_at=datetime.now(UTC)
    )
    update_input = UpdateBodyweightInput(weight_kg=Decimal("81.5"), notes="Updated notes")

    mock_uow.bodyweight_repository.get_by_id = AsyncMock(return_value=existing_log)
    mock_uow.bodyweight_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.update_bodyweight_log(log_id, update_input)

    # Assert
    assert result.weight_kg == Decimal("81.5")
    assert result.notes == "Updated notes"
    mock_uow.bodyweight_repository.update.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_bodyweight_log_not_found(service, mock_uow):
    # Arrange
    log_id = uuid4()
    mock_uow.bodyweight_repository.get_by_id = AsyncMock(return_value=None)
    update_input = UpdateBodyweightInput(weight_kg=Decimal("81.5"))

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.update_bodyweight_log(log_id, update_input)


@pytest.mark.asyncio
async def test_update_bodyweight_log_full_fields(service, mock_uow):
    # Arrange
    log_id = uuid4()
    existing_log = BodyweightLog(
        id=log_id, weight_kg=Decimal("80.0"), recorded_at=datetime.now(UTC)
    )
    new_time = datetime.now(UTC)
    update_input = UpdateBodyweightInput(
        weight_kg=Decimal("81.5"), recorded_at=new_time, notes="Updated notes"
    )

    mock_uow.bodyweight_repository.get_by_id = AsyncMock(return_value=existing_log)
    mock_uow.bodyweight_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.update_bodyweight_log(log_id, update_input)

    # Assert
    assert result.weight_kg == Decimal("81.5")
    assert result.recorded_at == new_time
    assert result.notes == "Updated notes"
    mock_uow.bodyweight_repository.update.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_bodyweight_log_not_found(service, mock_uow):
    # Arrange
    log_id = uuid4()
    mock_uow.bodyweight_repository.delete = AsyncMock(return_value=False)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.delete_bodyweight_log(log_id)
