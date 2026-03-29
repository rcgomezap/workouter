"""Unit tests for MuscleGroupService."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from workouter_cli.application.services.muscle_group_service import MuscleGroupService
from workouter_cli.domain.entities.exercise import MuscleGroup


@pytest.mark.asyncio
async def test_list_all_returns_all_muscle_groups() -> None:
    """Test that list_all returns all muscle groups from repository."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="id1", name="Chest"),
        MuscleGroup(id="id2", name="Back"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    result = await service.list_all()

    assert result == mock_groups
    repo.list_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_muscle_group_id_with_uuid() -> None:
    """Test resolving a valid UUID returns the UUID."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="550e8400-e29b-41d4-a716-446655440000", name="Chest"),
        MuscleGroup(id="550e8400-e29b-41d4-a716-446655440001", name="Back"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    result = await service.resolve_muscle_group_id("550e8400-e29b-41d4-a716-446655440000")

    assert result == "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.asyncio
async def test_resolve_muscle_group_id_with_name() -> None:
    """Test resolving by name (case-insensitive)."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="id1", name="Chest"),
        MuscleGroup(id="id2", name="Back"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    result = await service.resolve_muscle_group_id("chest")

    assert result == "id1"


@pytest.mark.asyncio
async def test_resolve_muscle_group_id_case_insensitive() -> None:
    """Test name resolution is case-insensitive."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="id1", name="Chest"),
        MuscleGroup(id="id2", name="Back"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    result = await service.resolve_muscle_group_id("CHEST")

    assert result == "id1"


@pytest.mark.asyncio
async def test_resolve_muscle_group_id_not_found_by_name() -> None:
    """Test ValueError raised when name not found."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="id1", name="Chest"),
        MuscleGroup(id="id2", name="Back"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    with pytest.raises(ValueError, match="Muscle group 'Legs' not found"):
        await service.resolve_muscle_group_id("Legs")


@pytest.mark.asyncio
async def test_resolve_muscle_group_id_not_found_by_uuid() -> None:
    """Test ValueError raised when UUID not found."""
    repo = AsyncMock()
    mock_groups = [
        MuscleGroup(id="550e8400-e29b-41d4-a716-446655440000", name="Chest"),
    ]
    repo.list_all = AsyncMock(return_value=mock_groups)
    service = MuscleGroupService(muscle_group_repository=repo)

    with pytest.raises(ValueError, match="Muscle group with ID"):
        await service.resolve_muscle_group_id("550e8400-e29b-41d4-a716-446655440099")
