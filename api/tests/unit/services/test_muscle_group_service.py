import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.application.services.muscle_group_service import MuscleGroupService
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return MuscleGroupService(mock_uow)


@pytest.mark.asyncio
async def test_get_muscle_groups(service, mock_uow):
    # Arrange
    mgs = [MuscleGroup(id=uuid4(), name="Chest"), MuscleGroup(id=uuid4(), name="Back")]
    mock_uow.muscle_group_repository.list = AsyncMock(return_value=mgs)

    # Act
    result = await service.get_muscle_groups()

    # Assert
    assert len(result) == 2
    assert result[0].name == "Chest"
    assert result[1].name == "Back"
    mock_uow.muscle_group_repository.list.assert_called_once_with(limit=100)


@pytest.mark.asyncio
async def test_get_muscle_group_success(service, mock_uow):
    # Arrange
    mg_id = uuid4()
    mg = MuscleGroup(id=mg_id, name="Quads")
    mock_uow.muscle_group_repository.get_by_id = AsyncMock(return_value=mg)

    # Act
    result = await service.get_muscle_group(mg_id)

    # Assert
    assert result.id == mg_id
    assert result.name == "Quads"
    mock_uow.muscle_group_repository.get_by_id.assert_called_once_with(mg_id)


@pytest.mark.asyncio
async def test_get_muscle_group_not_found(service, mock_uow):
    # Arrange
    mg_id = uuid4()
    mock_uow.muscle_group_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_muscle_group(mg_id)
