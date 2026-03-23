import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal

from app.application.services.session_service import SessionService
from app.application.dto.session import CreateSessionInput
from app.domain.entities.routine import Routine, RoutineExercise, RoutineSet
from app.domain.entities.exercise import Exercise
from app.domain.enums import SessionStatus, SetType


@pytest.mark.asyncio
async def test_create_session_from_routine():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    service = SessionService(mock_uow)

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
