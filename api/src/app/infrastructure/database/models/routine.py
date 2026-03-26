import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import SetType
from app.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.exercise import ExerciseTable
    from app.infrastructure.database.models.session import PlannedSessionTable, SessionTable


class RoutineTable(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "routine"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    routine_exercises: Mapped[list["RoutineExerciseTable"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan", order_by="RoutineExerciseTable.order"
    )
    planned_sessions: Mapped[list["PlannedSessionTable"]] = relationship(back_populates="routine")
    sessions: Mapped[list["SessionTable"]] = relationship(back_populates="routine")


class RoutineExerciseTable(Base, UUIDMixin):
    __tablename__ = "routine_exercise"
    __table_args__ = (UniqueConstraint("routine_id", "order"),)

    routine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routine.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercise.id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    superset_group: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    routine: Mapped[RoutineTable] = relationship(back_populates="routine_exercises")
    exercise: Mapped["ExerciseTable"] = relationship(back_populates="routine_exercises")
    routine_sets: Mapped[list["RoutineSetTable"]] = relationship(
        back_populates="routine_exercise", cascade="all, delete-orphan", order_by="RoutineSetTable.set_number"
    )


class RoutineSetTable(Base, UUIDMixin):
    __tablename__ = "routine_set"
    __table_args__ = (UniqueConstraint("routine_exercise_id", "set_number"),)

    routine_exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routine_exercise.id", ondelete="CASCADE"), nullable=False)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    set_type: Mapped[SetType] = mapped_column(Enum(SetType), nullable=False, default=SetType.STANDARD)
    target_reps_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_reps_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_rir: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2), nullable=True)
    weight_reduction_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    routine_exercise: Mapped[RoutineExerciseTable] = relationship(back_populates="routine_sets")
