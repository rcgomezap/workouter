from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dto.exercise import (
    CreateExerciseInput,
    MuscleGroupAssignmentInput,
    UpdateExerciseInput,
)
from app.application.dto.pagination import PaginationInput
from app.application.services.exercise_service import ExerciseService
from app.domain.entities.exercise import Exercise
from app.domain.entities.muscle_group import MuscleGroup
from app.domain.enums import MuscleRole
from app.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return ExerciseService(mock_uow)


@pytest.mark.asyncio
async def test_get_exercise_success(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    exercise = Exercise(id=ex_id, name="Bench Press", muscle_groups=[])
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=exercise)

    # Act
    result = await service.get_exercise(ex_id)

    # Assert
    assert result.id == ex_id
    assert result.name == "Bench Press"
    mock_uow.exercise_repository.get_by_id.assert_called_once_with(ex_id)


@pytest.mark.asyncio
async def test_get_exercise_not_found(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_exercise(ex_id)


@pytest.mark.asyncio
async def test_list_exercises(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    exercises = [
        Exercise(id=uuid4(), name="Squat", muscle_groups=[]),
        Exercise(id=uuid4(), name="Deadlift", muscle_groups=[]),
    ]
    mock_uow.exercise_repository.list = AsyncMock(return_value=exercises)
    mock_uow.exercise_repository.count = AsyncMock(return_value=2)

    # Act
    result = await service.list_exercises(pagination)

    # Assert
    assert len(result.items) == 2
    assert result.total == 2
    assert result.total_pages == 1
    mock_uow.exercise_repository.list.assert_called_once_with(offset=0, limit=10)
    mock_uow.exercise_repository.count.assert_called_once()


@pytest.mark.asyncio
async def test_create_exercise(service, mock_uow):
    # Arrange
    input_data = CreateExerciseInput(
        name="Lat Pulldown", description="Pull down the bar", equipment="Cable"
    )
    mock_uow.exercise_repository.add = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.create_exercise(input_data)

    # Assert
    assert result.name == "Lat Pulldown"
    assert result.description == "Pull down the bar"
    mock_uow.exercise_repository.add.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_exercise_full_fields(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    existing_ex = Exercise(id=ex_id, name="Old Name", muscle_groups=[])
    update_input = UpdateExerciseInput(
        name="New Name", description="New description", equipment="Dumbbell"
    )

    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=existing_ex)
    mock_uow.exercise_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.update_exercise(ex_id, update_input)

    # Assert
    assert result.name == "New Name"
    assert result.description == "New description"
    assert result.equipment == "Dumbbell"
    mock_uow.exercise_repository.update.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_exercise_not_found(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=None)
    update_input = UpdateExerciseInput(name="New Name")

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.update_exercise(ex_id, update_input)


@pytest.mark.asyncio
async def test_delete_exercise_not_found(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mock_uow.exercise_repository.delete = AsyncMock(return_value=False)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.delete_exercise(ex_id)


@pytest.mark.asyncio
async def test_assign_muscle_groups_exercise_not_found(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mg_id = uuid4()
    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=None)
    assignments = [MuscleGroupAssignmentInput(muscle_group_id=mg_id, role=MuscleRole.PRIMARY)]

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.assign_muscle_groups(ex_id, assignments)


@pytest.mark.asyncio
async def test_delete_exercise_success(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mock_uow.exercise_repository.delete = AsyncMock(return_value=True)
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.delete_exercise(ex_id)

    # Assert
    assert result is True
    mock_uow.exercise_repository.delete.assert_called_once_with(ex_id)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_assign_muscle_groups_success(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mg_id = uuid4()
    exercise = Exercise(id=ex_id, name="Bench Press", muscle_groups=[])
    mg = MuscleGroup(id=mg_id, name="Chest")

    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=exercise)
    mock_uow.muscle_group_repository.get_by_id = AsyncMock(return_value=mg)
    mock_uow.exercise_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    assignments = [MuscleGroupAssignmentInput(muscle_group_id=mg_id, role=MuscleRole.PRIMARY)]

    # Act
    result = await service.assign_muscle_groups(ex_id, assignments)

    # Assert
    assert len(result.muscle_groups) == 1
    assert result.muscle_groups[0].muscle_group.name == "Chest"
    assert result.muscle_groups[0].role == MuscleRole.PRIMARY
    mock_uow.exercise_repository.update.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_assign_muscle_groups_mg_not_found(service, mock_uow):
    # Arrange
    ex_id = uuid4()
    mg_id = uuid4()
    exercise = Exercise(id=ex_id, name="Bench Press", muscle_groups=[])

    mock_uow.exercise_repository.get_by_id = AsyncMock(return_value=exercise)
    mock_uow.muscle_group_repository.get_by_id = AsyncMock(return_value=None)

    assignments = [MuscleGroupAssignmentInput(muscle_group_id=mg_id, role=MuscleRole.PRIMARY)]

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.assign_muscle_groups(ex_id, assignments)
