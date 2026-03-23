import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal

from app.application.services.session_service import SessionService
from app.application.dto.session import CreateSessionInput, LogSetResultInput
from app.application.dto.pagination import PaginationInput
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.entities.exercise import Exercise
from app.domain.entities.session import Session, SessionSet
from app.domain.enums import SessionStatus, SetType
from app.domain.exceptions import EntityNotFoundException, ConflictException


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def service(mock_uow):
    return SessionService(mock_uow)


@pytest.mark.asyncio
async def test_get_session_success(service, mock_uow):
    # Arrange
    session_id = uuid4()
    session = Session(id=session_id, status=SessionStatus.PLANNED)
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=session)

    # Act
    result = await service.get_session(session_id)

    # Assert
    assert result.id == session_id
    mock_uow.session_repository.get_by_id.assert_called_once_with(session_id)


@pytest.mark.asyncio
async def test_get_session_not_found(service, mock_uow):
    # Arrange
    session_id = uuid4()
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_session(session_id)


@pytest.mark.asyncio
async def test_list_sessions(service, mock_uow):
    # Arrange
    pagination = PaginationInput(page=1, page_size=10)
    sessions = [Session(id=uuid4()), Session(id=uuid4())]
    mock_uow.session_repository.list = AsyncMock(return_value=sessions)

    # Act
    result = await service.list_sessions(pagination)

    # Assert
    assert len(result.items) == 2
    mock_uow.session_repository.list.assert_called_once_with(offset=0, limit=10)


@pytest.mark.asyncio
async def test_create_session_from_routine(service, mock_uow):

    routine_id = uuid4()
    exercise_id = uuid4()

    exercise = Exercise(id=exercise_id, name="Squat", muscle_groups=[])

    routine_set = RoutineSet(
        id=uuid4(),
        set_number=1,
        set_type=SetType.STANDARD,
        target_reps_max=10,
        target_rir=2,
        target_weight_kg=Decimal("100.0"),
    )

    routine_exercise = RoutineExercise(id=uuid4(), exercise=exercise, order=1, sets=[routine_set])

    routine = Routine(id=routine_id, name="Leg Day", exercises=[routine_exercise])

    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=routine)
    mock_uow.session_repository.add = AsyncMock()
    mock_uow.commit = AsyncMock()

    input_dto = CreateSessionInput(routine_id=routine_id)

    # Act
    result = await service.create_session(input_dto)

    # Assert
    assert result.routine_id == routine_id
    assert result.status == SessionStatus.PLANNED
    assert len(result.exercises) == 1

    session_exercise = result.exercises[0]
    assert session_exercise.exercise.id == exercise_id
    assert len(session_exercise.sets) == 1

    session_set = session_exercise.sets[0]
    assert session_set.set_number == 1
    assert session_set.target_reps == 10
    assert session_set.target_rir == 2
    assert session_set.target_weight_kg == Decimal("100.0")

    mock_uow.session_repository.add.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_start_session_success(service, mock_uow):
    # Arrange
    session_id = uuid4()
    session = Session(id=session_id, status=SessionStatus.PLANNED)
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=session)
    mock_uow.session_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.start_session(session_id)

    # Assert
    assert result.status == SessionStatus.IN_PROGRESS
    assert result.started_at is not None
    mock_uow.session_repository.update.assert_called_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_start_session_conflict(service, mock_uow):
    # Arrange
    session_id = uuid4()
    session = Session(id=session_id, status=SessionStatus.COMPLETED)
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=session)

    # Act & Assert
    with pytest.raises(ConflictException):
        await service.start_session(session_id)


@pytest.mark.asyncio
async def test_complete_session_success(service, mock_uow):
    # Arrange
    session_id = uuid4()
    session = Session(id=session_id, status=SessionStatus.IN_PROGRESS)
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=session)
    mock_uow.session_repository.update = AsyncMock()
    mock_uow.commit = AsyncMock()

    # Act
    result = await service.complete_session(session_id)

    # Assert
    assert result.status == SessionStatus.COMPLETED
    assert result.completed_at is not None
    mock_uow.session_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_log_set_result_success(service, mock_uow):
    # Arrange
    set_id = uuid4()
    session_set = SessionSet(id=set_id, set_number=1, set_type=SetType.STANDARD)
    mock_uow.session_repository.get_set_by_id = AsyncMock(return_value=session_set)
    mock_uow.session_repository.update_set = AsyncMock()
    mock_uow.commit = AsyncMock()

    input_data = LogSetResultInput(actual_reps=10, actual_weight_kg=Decimal("100.0"), actual_rir=2)

    # Act
    result = await service.log_set_result(set_id, input_data)

    # Assert
    assert result.actual_reps == 10
    assert result.actual_weight_kg == Decimal("100.0")
    mock_uow.session_repository.update_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_not_found_error(service, mock_uow):
    # Arrange
    session_id = uuid4()
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.get_session(session_id)


@pytest.mark.asyncio
async def test_start_session_not_found(service, mock_uow):
    # Arrange
    session_id = uuid4()
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.start_session(session_id)


@pytest.mark.asyncio
async def test_complete_session_not_found(service, mock_uow):
    # Arrange
    session_id = uuid4()
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=None)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.complete_session(session_id)


@pytest.mark.asyncio
async def test_complete_session_conflict(service, mock_uow):
    # Arrange
    session_id = uuid4()
    session = Session(id=session_id, status=SessionStatus.PLANNED)
    mock_uow.session_repository.get_by_id = AsyncMock(return_value=session)

    # Act & Assert
    with pytest.raises(ConflictException):
        await service.complete_session(session_id)


@pytest.mark.asyncio
async def test_log_set_result_not_found(service, mock_uow):
    # Arrange
    set_id = uuid4()
    mock_uow.session_repository.get_set_by_id = AsyncMock(return_value=None)
    input_data = LogSetResultInput(actual_reps=10, actual_weight_kg=Decimal("100.0"), actual_rir=2)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.log_set_result(set_id, input_data)


@pytest.mark.asyncio
async def test_create_session_routine_not_found(service, mock_uow):
    # Arrange
    routine_id = uuid4()
    mock_uow.routine_repository.get_by_id = AsyncMock(return_value=None)
    input_dto = CreateSessionInput(routine_id=routine_id)

    # Act & Assert
    with pytest.raises(EntityNotFoundException):
        await service.create_session(input_dto)
