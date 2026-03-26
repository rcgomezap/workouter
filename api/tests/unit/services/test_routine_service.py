from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dto.pagination import PaginationInput
from app.application.dto.routine import (
    AddRoutineExerciseInput,
    CreateRoutineInput,
    UpdateRoutineInput,
)
from app.application.services.routine_service import RoutineService
from app.domain.entities.exercise import Exercise
from app.domain.entities.routine import Routine
from app.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return RoutineService(mock_uow)


@pytest.mark.asyncio
async def test_get_routine_success(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    routine = Routine(id=routine_id, name="Leg Day", description="Don't skip")
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=routine)

    # Act
    result = await service.get_routine(routine_id)

    # Assert
    assert result.id == routine_id
    assert result.name == "Leg Day"
    mock_uow.routine_repository.get_by_id.assert_called_once_with(routine_id)


@pytest.mark.asyncio
async def test_get_routine_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_routine(routine_id)


@pytest.mark.asyncio
async def test_list_routines(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    routines = [Routine(id=uuid4(), name="Upper"), Routine(id=uuid4(), name="Lower")]
    mock_uow.routine_repository.list = AsyncMock(return_value=routines)
    mock_uow.routine_repository.count = AsyncMock(return_value=2)

    # Act
    result = await service.list_routines(pagination)

    # Assert
    assert len(result.items) == 2
    assert result.total == 2
    assert result.total_pages == 1
    mock_uow.routine_repository.list.assert_called_once_with(offset=0, limit=10)
    mock_uow.routine_repository.count.assert_called_once()


@pytest.mark.asyncio
async def test_create_routine(service, mock_uow):
    # Arrange
    input_data = CreateRoutineInput(name="Push", description="Shoulder focus")
    mock_uow.routine_repository.add = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.create_routine(input_data)

    # Assert
    assert result.name == "Push"
    mock_uow.routine_repository.add.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_routine_success(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    existing_routine = Routine(id=routine_id, name="Old Name")
    update_input = UpdateRoutineInput(name="New Name", description="New desc")

    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=existing_routine)
    mock_uow.routine_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.update_routine(routine_id, update_input)

    # Assert
    assert result.name == "New Name"
    assert result.description == "New desc"
    mock_uow.routine_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_routine_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=None)
    update_input = UpdateRoutineInput(name="New Name")

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.update_routine(routine_id, update_input)


@pytest.mark.asyncio
async def test_delete_routine_success(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    mock_uow.routine_repository.delete = AsyncMock(return_value=True)
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.delete_routine(routine_id)

    # Assert
    assert result is True
    mock_uow.routine_repository.delete.assert_called_once_with(routine_id)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_routine_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    mock_uow.routine_repository.delete = AsyncMock(return_value=False)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.delete_routine(routine_id)


@pytest.mark.asyncio
async def test_add_exercise_success(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    ex_id = uuid4()
    routine = Routine(id=routine_id, name="Full Body")
    exercise = Exercise(id=ex_id, name="Squat", muscle_groups=[])

    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=routine)
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=exercise)
    mock_uow.routine_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    input_data = AddRoutineExerciseInput(exercise_id=ex_id, order=1)

    # Act
    result = await service.add_exercise(routine_id, input_data)

    # Assert
    assert len(result.exercises) == 1
    assert result.exercises[0].exercise.name == "Squat"
    mock_uow.routine_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_add_exercise_routine_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    ex_id = uuid4()
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=None)
    input_data = AddRoutineExerciseInput(exercise_id=ex_id, order=1)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.add_exercise(routine_id, input_data)


@pytest.mark.asyncio
async def test_add_exercise_exercise_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    ex_id = uuid4()
    routine = Routine(id=routine_id, name="Full Body")
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=routine)
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=None)
    input_data = AddRoutineExerciseInput(exercise_id=ex_id, order=1)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.add_exercise(routine_id, input_data)
