"""Muscle group application service."""

from __future__ import annotations

from collections.abc import Sequence

from workouter_cli.domain.entities.exercise import MuscleGroup
from workouter_cli.domain.repositories.muscle_group import MuscleGroupRepository


class MuscleGroupService:
    """Muscle group use-cases orchestration."""

    def __init__(self, muscle_group_repository: MuscleGroupRepository) -> None:
        self.muscle_group_repository = muscle_group_repository

    async def list_all(self) -> list[MuscleGroup]:
        """List all muscle groups."""
        return await self.muscle_group_repository.list_all()

    async def resolve_muscle_group_ids(self, names_or_ids: Sequence[str]) -> list[str]:
        """Resolve many muscle group names/UUIDs to UUIDs with one lookup."""
        all_groups = await self.list_all()
        return self.resolve_muscle_group_ids_from_catalog(names_or_ids, all_groups)

    async def resolve_muscle_group_id(self, name_or_id: str) -> str:
        """
        Resolve muscle group name or UUID to UUID.

        Args:
            name_or_id: Muscle group name (case-insensitive) or UUID

        Returns:
            UUID string

        Raises:
            ValueError: If muscle group not found or name is ambiguous
        """
        all_groups = await self.list_all()
        return self._resolve_muscle_group_id_from_catalog(name_or_id, all_groups)

    def resolve_muscle_group_ids_from_catalog(
        self,
        names_or_ids: Sequence[str],
        all_groups: Sequence[MuscleGroup],
    ) -> list[str]:
        """Resolve many muscle group names/UUIDs from a pre-fetched list."""
        return [
            self._resolve_muscle_group_id_from_catalog(value, all_groups) for value in names_or_ids
        ]

    def _resolve_muscle_group_id_from_catalog(
        self,
        name_or_id: str,
        all_groups: Sequence[MuscleGroup],
    ) -> str:
        """Resolve one muscle group from a pre-fetched list."""
        # Check if it's already a valid UUID format
        if self._is_uuid_format(name_or_id):
            if any(group.id == name_or_id for group in all_groups):
                return name_or_id
            raise ValueError(f"Muscle group with ID '{name_or_id}' not found")

        # Try to find by name (case-insensitive)
        matches = [g for g in all_groups if g.name.lower() == name_or_id.lower()]

        if len(matches) == 0:
            raise ValueError(
                f"Muscle group '{name_or_id}' not found. "
                f"Use 'muscle-groups list' to see available groups."
            )

        if len(matches) > 1:
            # This shouldn't happen with unique names in DB, but handle it
            raise ValueError(f"Ambiguous muscle group name '{name_or_id}'")

        return matches[0].id

    @staticmethod
    def _is_uuid_format(value: str) -> bool:
        """Check if string looks like a UUID."""
        import re

        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
        )
        return bool(uuid_pattern.match(value))
