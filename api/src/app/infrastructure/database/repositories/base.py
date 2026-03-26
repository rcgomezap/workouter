from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.base import BaseRepository

T = TypeVar("T")
M = TypeVar("M")


class SQLAlchemyBaseRepository(Generic[T, M], BaseRepository[T]):
    def __init__(self, session: AsyncSession, model_class: type[M]):
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, id: UUID) -> T | None:
        result = await self._session.get(self._model_class, id)
        if result:
            return self._to_domain(result)
        return None

    async def list(self, offset: int = 0, limit: int = 20) -> Sequence[T]:
        stmt = select(self._model_class).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._model_class)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def add(self, entity: T) -> T:
        model_obj = self._to_model(entity)
        self._session.add(model_obj)
        # Flush to get the ID and other generated fields if needed
        # But we usually commit at UoW level.
        # For now, let's assume we want the updated entity back.
        await self._session.flush()
        await self._session.refresh(model_obj)
        return self._to_domain(model_obj)

    async def update(self, entity: T) -> T:
        # In SQLAlchemy, we usually get, update attributes, and flush.
        # This implementation might vary depending on how the domain entity is used.
        # If the entity is a detached model or a separate DTO-like object.
        # Assuming we need to merge or manually update.
        stmt = select(self._model_class).where(self._model_class.id == entity.id)  # type: ignore
        # Try to use any specific loading options defined in subclasses if needed
        # but for now let's just use the basic select
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()

        if not model_obj:
            raise ValueError(f"Entity with id {entity.id} not found")  # type: ignore

        self._update_model(model_obj, entity)
        await self._session.flush()
        await self._session.refresh(model_obj)
        return self._to_domain(model_obj)

    async def delete(self, id: UUID) -> bool:
        stmt = delete(self._model_class).where(self._model_class.id == id)  # type: ignore
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    def _to_domain(self, model_obj: M) -> T:
        raise NotImplementedError

    def _to_model(self, entity: T) -> M:
        raise NotImplementedError

    def _update_model(self, model_obj: M, entity: T) -> None:
        raise NotImplementedError
