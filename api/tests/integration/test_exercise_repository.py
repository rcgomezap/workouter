import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.exercise import Exercise
from app.domain.entities.muscle_group import MuscleGroup
from app.infrastructure.database.repositories.exercise import SQLAlchemyExerciseRepository
from app.infrastructure.database.repositories.muscle_group import SQLAlchemyMuscleGroupRepository
from app.infrastructure.database.models.exercise import exercise_muscle_group
from sqlalchemy import insert


@pytest.mark.asyncio
async def test_exercise_repository_crud(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyExerciseRepository(db_session)
    exercise = Exercise(
        id=uuid4(),
        name="Bench Press",
        description="Chest exercise",
        equipment="Barbell",
        muscle_groups=[],
    )

    # Act - Add
    added = await repo.add(exercise)
    assert added.name == "Bench Press"

    # Act - Get
    fetched = await repo.get_by_id(exercise.id)
    assert fetched is not None
    assert fetched.name == "Bench Press"

    # Act - List
    all_exercises = await repo.list()
    assert len(all_exercises) >= 1
    assert any(e.name == "Bench Press" for e in all_exercises)

    # Act - Update
    exercise.name = "Incline Bench Press"
    updated = await repo.update(exercise)
    assert updated.name == "Incline Bench Press"

    # Act - Delete
    success = await repo.delete(exercise.id)
    assert success is True
    assert await repo.get_by_id(exercise.id) is None


@pytest.mark.asyncio
async def test_exercise_repository_filter_by_muscle_group(db_session: AsyncSession):
    # Arrange
    ex_repo = SQLAlchemyExerciseRepository(db_session)
    mg_repo = SQLAlchemyMuscleGroupRepository(db_session)

    mg = MuscleGroup(id=uuid4(), name="Chest")
    await mg_repo.add(mg)

    ex1 = Exercise(id=uuid4(), name="Pushup", muscle_groups=[])
    ex2 = Exercise(id=uuid4(), name="Squat", muscle_groups=[])
    await ex_repo.add(ex1)
    await ex_repo.add(ex2)

    # Manually insert association for testing list_by_muscle_group
    # (since the repo _to_model doesn't handle associations yet)
    await db_session.execute(
        insert(exercise_muscle_group).values(
            exercise_id=ex1.id, muscle_group_id=mg.id, role="primary"
        )
    )
    await db_session.commit()

    # Act
    chest_exercises = await ex_repo.list_by_muscle_group(mg.id)
    count = await ex_repo.count_by_muscle_group(mg.id)
    total_count = await ex_repo.count_total()

    # Assert
    assert len(chest_exercises) == 1
    assert chest_exercises[0].name == "Pushup"
    assert count == 1
    assert total_count >= 2
