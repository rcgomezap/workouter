from datetime import datetime, date
from typing import TYPE_CHECKING
import uuid
from decimal import Decimal
from sqlalchemy import ForeignKey, Text, Integer, Date, Enum, UniqueConstraint, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.enums import SessionStatus, SetType
from app.infrastructure.database.models.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.infrastructure.database.models.mesocycle import MesocycleTable, MesocycleWeekTable
    from app.infrastructure.database.models.routine import RoutineTable
    from app.infrastructure.database.models.exercise import ExerciseTable


class PlannedSessionTable(Base, UUIDMixin):
    __tablename__ = "planned_session"
    __table_args__ = (UniqueConstraint("mesocycle_week_id", "date"),)

    mesocycle_week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mesocycle_week.id", ondelete="CASCADE"), nullable=False
    )
    routine_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("routine.id", ondelete="SET NULL"), nullable=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    mesocycle_week: Mapped["MesocycleWeekTable"] = relationship(back_populates="planned_sessions")
    routine: Mapped["RoutineTable"] = relationship(back_populates="planned_sessions")
    session: Mapped["SessionTable"] = relationship(back_populates="planned_session")


class SessionTable(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "session"

    planned_session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("planned_session.id"), nullable=True
    )
    mesocycle_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("mesocycle.id"), nullable=True
    )
    routine_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("routine.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), nullable=False, default=SessionStatus.PLANNED
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    planned_session: Mapped[PlannedSessionTable | None] = relationship(back_populates="session")
    mesocycle: Mapped["MesocycleTable | None"] = relationship(back_populates="sessions")
    routine: Mapped["RoutineTable | None"] = relationship(back_populates="sessions")
    session_exercises: Mapped[list["SessionExerciseTable"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionExerciseTable.order",
    )


class SessionExerciseTable(Base, UUIDMixin):
    __tablename__ = "session_exercise"
    __table_args__ = (UniqueConstraint("session_id", "order"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("session.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercise.id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    superset_group: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped[SessionTable] = relationship(back_populates="session_exercises")
    exercise: Mapped["ExerciseTable"] = relationship(back_populates="session_exercises")
    session_sets: Mapped[list["SessionSetTable"]] = relationship(
        back_populates="session_exercise",
        cascade="all, delete-orphan",
        order_by="SessionSetTable.set_number",
    )


class SessionSetTable(Base, UUIDMixin):
    __tablename__ = "session_set"
    __table_args__ = (UniqueConstraint("session_exercise_id", "set_number"),)

    session_exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("session_exercise.id", ondelete="CASCADE"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    set_type: Mapped[SetType] = mapped_column(Enum(SetType), nullable=False)
    target_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_rir: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    actual_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_rir: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    weight_reduction_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    performed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    session_exercise: Mapped[SessionExerciseTable] = relationship(back_populates="session_sets")
