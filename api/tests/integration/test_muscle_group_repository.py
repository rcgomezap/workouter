import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.muscle_group import MuscleGroup
from app.infrastructure.database.repositories.muscle_group import SQLAlchemyMuscleGroupRepository


@pytest.mark.asyncio
async def test_muscle_group_repository_add_and_get(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyMuscleGroupRepository(db_session)
    mg = MuscleGroup(id=uuid4(), name="Quads")

    # Act
    added_mg = await repo.add(mg)
    fetched_mg = await repo.get_by_id(mg.id)

    # Assert
    assert added_mg.name == "Quads"
    assert fetched_mg is not None
    assert fetched_mg.name == "Quads"
    assert fetched_mg.id == mg.id


@pytest.mark.asyncio
async def test_muscle_group_repository_list(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyMuscleGroupRepository(db_session)
    await repo.add(MuscleGroup(id=uuid4(), name="Chest"))
    await repo.add(MuscleGroup(id=uuid4(), name="Back"))

    # Act
    mgs = await repo.list_all()

    # Assert
    assert len(mgs) >= 2
    names = [mg.name for mg in mgs]
    assert "Chest" in names
    assert "Back" in names
    # list_all orders by name
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_muscle_group_repository_get_by_name(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyMuscleGroupRepository(db_session)
    name = f"Shoulders_{uuid4()}"
    await repo.add(MuscleGroup(id=uuid4(), name=name))

    # Act
    mg = await repo.get_by_name(name)

    # Assert
    assert mg is not None
    assert mg.name == name


@pytest.mark.asyncio
async def test_muscle_group_repository_update(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyMuscleGroupRepository(db_session)
    mg = MuscleGroup(id=uuid4(), name="Biceps")
    await repo.add(mg)

    mg.name = "Triceps"

    # Act
    updated_mg = await repo.update(mg)
    fetched_mg = await repo.get_by_id(mg.id)

    # Assert
    assert updated_mg.name == "Triceps"
    assert fetched_mg.name == "Triceps"


@pytest.mark.asyncio
async def test_muscle_group_repository_delete(db_session: AsyncSession):
    # Arrange
    repo = SQLAlchemyMuscleGroupRepository(db_session)
    mg = MuscleGroup(id=uuid4(), name="Calves")
    await repo.add(mg)

    # Act
    success = await repo.delete(mg.id)
    fetched_mg = await repo.get_by_id(mg.id)

    # Assert
    assert success is True
    assert fetched_mg is None
