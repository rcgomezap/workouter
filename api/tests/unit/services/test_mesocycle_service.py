import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import date

from app.application.services.mesocycle_service import MesocycleService
from app.application.dto.mesocycle import CreateMesocycleInput, UpdateMesocycleInput
from app.application.dto.pagination import PaginationInput
from app.domain.entities.mesocycle import Mesocycle, MesocycleWeek, PlannedSession
from app.domain.enums import MesocycleStatus, WeekType
from app.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return MesocycleService(mock_uow)


@pytest.mark.asyncio
async def test_get_mesocycle_success(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    meso = Mesocycle(
        id=meso_id,
        name="Hypertrophy Block",
        start_date=date(2026, 1, 1),
        status=MesocycleStatus.ACTIVE,
    )
    mock_uow.mesocycle_repository.get_by_id = AsyncMock(return_value=meso)

    # Act
    result = await service.get_mesocycle(meso_id)

    # Assert
    assert result.id == meso_id
    assert result.name == "Hypertrophy Block"
    mock_uow.mesocycle_repository.get_by_id.assert_called_once_with(meso_id)


@pytest.mark.asyncio
async def test_get_mesocycle_not_found(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    mock_uow.mesocycle_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_mesocycle(meso_id)


@pytest.mark.asyncio
async def test_list_mesocycles(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    mesos = [
        Mesocycle(id=uuid4(), name="Meso 1", start_date=date(2026, 1, 1)),
        Mesocycle(id=uuid4(), name="Meso 2", start_date=date(2026, 2, 1)),
    ]
    mock_uow.mesocycle_repository.list = AsyncMock(return_value=mesos)
    mock_uow.mesocycle_repository.count_total = AsyncMock(return_value=len(mesos))

    # Act
    result = await service.list_mesocycles(pagination)

    # Assert
    assert len(result.items) == 2
    mock_uow.mesocycle_repository.list.assert_called_once_with(offset=0, limit=10)


@pytest.mark.asyncio
async def test_create_mesocycle(service, mock_uow):
    # Arrange
    input_data = CreateMesocycleInput(
        name="Strength Block", description="Focus on compound lifts", start_date=date(2026, 3, 1)
    )
    mock_uow.mesocycle_repository.add = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.create_mesocycle(input_data)

    # Assert
    assert result.name == "Strength Block"
    mock_uow.mesocycle_repository.add.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_mesocycle_full_fields(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    existing_meso = Mesocycle(id=meso_id, name="Old Name", start_date=date(2026, 1, 1))
    update_input = UpdateMesocycleInput(
        name="New Name",
        description="New description",
        start_date=date(2026, 2, 1),
        end_date=date(2026, 3, 1),
        status=MesocycleStatus.COMPLETED,
    )

    mock_uow.mesocycle_repository.get_by_id = AsyncMock(return_value=existing_meso)
    mock_uow.mesocycle_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.update_mesocycle(meso_id, update_input)

    # Assert
    assert result.name == "New Name"
    assert result.start_date == date(2026, 2, 1)
    assert result.end_date == date(2026, 3, 1)
    assert result.status == MesocycleStatus.COMPLETED
    mock_uow.mesocycle_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_mesocycle_not_found(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    mock_uow.mesocycle_repository.get_by_id = AsyncMock(return_value=None)
    update_input = UpdateMesocycleInput(name="New Name")

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.update_mesocycle(meso_id, update_input)


@pytest.mark.asyncio
async def test_delete_mesocycle_success(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    mock_uow.mesocycle_repository.delete = AsyncMock(return_value=True)
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.delete_mesocycle(meso_id)

    # Assert
    assert result is True
    mock_uow.mesocycle_repository.delete.assert_called_once_with(meso_id)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_mesocycle_not_found(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    mock_uow.mesocycle_repository.delete = AsyncMock(return_value=False)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.delete_mesocycle(meso_id)


@pytest.mark.asyncio
async def test_mesocycle_with_weeks_mapping(service, mock_uow):
    # Arrange
    meso_id = uuid4()
    week = MesocycleWeek(
        id=uuid4(),
        week_number=1,
        week_type=WeekType.TRAINING,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 7),
    )
    meso = Mesocycle(id=meso_id, name="Meso with weeks", start_date=date(2026, 1, 1), weeks=[week])
    mock_uow.mesocycle_repository.get_by_id = AsyncMock(return_value=meso)

    # Act
    result = await service.get_mesocycle(meso_id)

    # Assert
    assert len(result.weeks) == 1
    assert result.weeks[0].week_number == 1
