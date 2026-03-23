from datetime import date
from typing import Sequence
from uuid import UUID
from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.entities.session import Session
from app.domain.enums import SessionStatus
from app.domain.repositories.session import SessionRepository
from app.infrastructure.database.models.session import (
    SessionTable,
    SessionExerciseTable,
    SessionSetTable,
    PlannedSessionTable,
)
from app.infrastructure.database.repositories.base import SQLAlchemyBaseRepository


class SQLAlchemySessionRepository(
    SQLAlchemyBaseRepository[Session, SessionTable], SessionRepository
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SessionTable)

    async def get_by_id(self, id: UUID) -> Session | None:
        stmt = (
            select(SessionTable)
            .where(SessionTable.id == id)
            .options(
                selectinload(SessionTable.session_exercises).selectinload(
                    SessionExerciseTable.session_sets
                ),
                selectinload(SessionTable.session_exercises).selectinload(
                    SessionExerciseTable.exercise
                ),
                selectinload(SessionTable.planned_session),
                selectinload(SessionTable.mesocycle),
                selectinload(SessionTable.routine),
            )
        )
        result = await self._session.execute(stmt)
        model_obj = result.scalar_one_or_none()
        if model_obj:
            return self._to_domain(model_obj)
        return None

    async def list_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Session]:
        stmt = select(SessionTable).offset(offset).limit(limit).order_by(SessionTable.started_at.desc())
        
        filters = []
        if status:
            filters.append(SessionTable.status == status)
        if mesocycle_id:
            filters.append(SessionTable.mesocycle_id == mesocycle_id)
        if date_from:
            filters.append(cast(SessionTable.started_at, Date) >= date_from)
        if date_to:
            filters.append(cast(SessionTable.started_at, Date) <= date_to)
            
        if filters:
            stmt = stmt.where(and_(*filters))
            
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_by_filters(
        self,
        status: SessionStatus | None = None,
        mesocycle_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(SessionTable)
        
        filters = []
        if status:
            filters.append(SessionTable.status == status)
        if mesocycle_id:
            filters.append(SessionTable.mesocycle_id == mesocycle_id)
        if date_from:
            filters.append(cast(SessionTable.started_at, Date) >= date_from)
        if date_to:
            filters.append(cast(SessionTable.started_at, Date) <= date_to)
            
        if filters:
            stmt = stmt.where(and_(*filters))
            
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> Sequence[Session]:
        stmt = select(SessionTable).where(
            and_(
                cast(SessionTable.started_at, Date) >= start_date,
                cast(SessionTable.started_at, Date) <= end_date
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    def _to_domain(self, model_obj: SessionTable) -> Session:
        return Session.model_validate(model_obj)

    def _to_model(self, entity: Session) -> SessionTable:
        return SessionTable(
            id=entity.id,
            planned_session_id=entity.planned_session_id,
            mesocycle_id=entity.mesocycle_id,
            routine_id=entity.routine_id,
            status=entity.status,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model(self, model_obj: SessionTable, entity: Session) -> None:
        model_obj.status = entity.status
        model_obj.started_at = entity.started_at
        model_obj.completed_at = entity.completed_at
        model_obj.notes = entity.notes
        model_obj.updated_at = entity.updated_at
