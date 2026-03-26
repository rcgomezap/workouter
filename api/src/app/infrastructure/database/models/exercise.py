from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import MuscleRole
from app.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.muscle_group import MuscleGroupTable
    from app.infrastructure.database.models.routine import RoutineExerciseTable
    from app.infrastructure.database.models.session import SessionExerciseTable


# Association table for Exercise and MuscleGroup
exercise_muscle_group = Table(
    "exercise_muscle_group",
    Base.metadata,
    Column("exercise_id", ForeignKey("exercise.id", ondelete="CASCADE"), primary_key=True),
    Column("muscle_group_id", ForeignKey("muscle_group.id"), primary_key=True),
    Column("role", Enum(MuscleRole), nullable=False),
)


class ExerciseTable(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exercise"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    muscle_groups: Mapped[list["MuscleGroupTable"]] = relationship(
        secondary=exercise_muscle_group, back_populates="exercises"
    )
    routine_exercises: Mapped[list["RoutineExerciseTable"]] = relationship(
        back_populates="exercise"
    )
    session_exercises: Mapped[list["SessionExerciseTable"]] = relationship(
        back_populates="exercise"
    )
