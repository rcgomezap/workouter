from typing import Generic, TypeVar, Protocol, Sequence
from uuid import UUID

T = TypeVar("T")


class BaseRepository(Protocol[T]):
    async def get_by_id(self, id: UUID) -> T | None:
        ...

    async def list(self, offset: int = 0, limit: int = 20) -> Sequence[T]:
        ...

    async def add(self, entity: T) -> T:
        ...

    async def update(self, entity: T) -> T:
        ...

    async def delete(self, id: UUID) -> bool:
        ...
