from uuid import UUID

from app.application.dto.exercise import MuscleGroupDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import EntityNotFoundException


class MuscleGroupService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_muscle_groups(self) -> list[MuscleGroupDTO]:
        async with self.uow:
            muscle_groups = await self.uow.muscle_group_repository.list(limit=100)
            return [MuscleGroupDTO(id=mg.id, name=mg.name) for mg in muscle_groups]

    async def get_muscle_group(self, id: UUID) -> MuscleGroupDTO:
        async with self.uow:
            mg = await self.uow.muscle_group_repository.get_by_id(id)
            if not mg:
                raise EntityNotFoundException("MuscleGroup", id)
            return MuscleGroupDTO(id=mg.id, name=mg.name)
