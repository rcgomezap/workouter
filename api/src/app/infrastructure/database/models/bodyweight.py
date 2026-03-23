from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import Text, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.models.base import Base, UUIDMixin


class BodyweightLogTable(Base, UUIDMixin):
    __tablename__ = "bodyweight_log"

    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
