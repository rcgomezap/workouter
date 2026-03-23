from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base, UUIDMixin
from app.infrastructure.database.models.exercise import exercise_muscle_group


if TYPE_CHECKING:
    from app.infrastructure.database.models.exercise import ExerciseTable


class MuscleGroupTable(Base, UUIDMixin):
    __tablename__ = "muscle_group"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relationships
    exercises: Mapped[list["ExerciseTable"]] = relationship(
        secondary=exercise_muscle_group, back_populates="muscle_groups"
    )
