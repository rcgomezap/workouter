import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import MesocycleStatus, WeekType
from app.infrastructure.database.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.session import PlannedSessionTable, SessionTable


class MesocycleTable(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mesocycle"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[MesocycleStatus] = mapped_column(
        Enum(MesocycleStatus), nullable=False, default=MesocycleStatus.PLANNED
    )

    # Relationships
    weeks: Mapped[list["MesocycleWeekTable"]] = relationship(
        back_populates="mesocycle",
        cascade="all, delete-orphan",
        order_by="MesocycleWeekTable.week_number",
    )
    sessions: Mapped[list["SessionTable"]] = relationship(back_populates="mesocycle")


class MesocycleWeekTable(Base, UUIDMixin):
    __tablename__ = "mesocycle_week"
    __table_args__ = (UniqueConstraint("mesocycle_id", "week_number"),)

    mesocycle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mesocycle.id", ondelete="CASCADE"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    week_type: Mapped[WeekType] = mapped_column(Enum(WeekType), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    mesocycle: Mapped[MesocycleTable] = relationship(back_populates="weeks")
    planned_sessions: Mapped[list["PlannedSessionTable"]] = relationship(
        back_populates="mesocycle_week", cascade="all, delete-orphan"
    )
